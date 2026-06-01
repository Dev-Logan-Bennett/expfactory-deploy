import datetime
import os
import sys
from pathlib import Path

from .utils import generate_experiment_context
import web
from web.contrib.template import render_jinja

from .preprocess import raw_to_df
from .config import build_parser, RunConfig
from . import storage
from .paths import should_write_bids

web.config.debug = False

package_dir = os.path.dirname(os.path.abspath(__file__))

urls = ("/", "serve", "/serve", "serve", "/decline", "decline", "/reset", "reset")

app = web.application(urls, globals())


# Function to create a session with unique storage based on port
def get_session(port=8080):
    session_path = Path(package_dir, f"sessions_{port}")
    session_path.mkdir(exist_ok=True)
    return web.session.Session(
        app,
        web.session.DiskStore(session_path),
        initializer={"incomplete": None},
    )


# Default session - will be replaced in run()
session = get_session()


parser = build_parser()

experiments = []

template_dir = Path(package_dir, "templates")
static_dir = Path(package_dir, "static/")
experiments_dir = Path(static_dir, "experiments/")
render = render_jinja(template_dir, encoding="utf-8")


def run(args=None):
    args = parser.parse_args(args)
    if args.exps is not None:
        experiments = args.exps
    elif args.config is not None:
        if args.config.is_file():
            with open(args.config) as fp:
                experiments = [Path(x.strip()) for x in fp.readlines()]
        else:
            experiments = [args.config]
    else:
        parser.print_help()
        sys.exit()

    experiments = [e.absolute() for e in experiments if e.exists()]

    if len(experiments) == 0:
        print("No Experiments Found")
        sys.exit()

    for experiment in experiments:
        try:
            os.mkdir(experiments_dir)
        except FileExistsError:
            pass
        try:
            os.symlink(experiment, Path(experiments_dir, experiment.stem))
        except FileExistsError:
            os.unlink(Path(experiments_dir, experiment.stem))
            os.symlink(experiment, Path(experiments_dir, experiment.stem))

    web.config.update({"experiments": experiments})
    web.config.run_config = RunConfig.from_args(args)
    if args.group_index is not None:
        web.config.update({"group_index": args.group_index})

    # webpy is opinionated about sys.argv. Set it to something it can handle
    port = 8080
    sys.argv = [None, str(port)]

    started = False
    while port < 10000 and not started:
        try:
            # Update session with port-specific storage
            global session
            session = get_session(port)

            sys.argv = [None, str(port)]
            print(f"Starting server on port {port}")
            app.run()
            started = True
        except OSError as e:
            print(f"Port {port} is in use, trying next port...")
            port += 1
            sys.argv = [None, str(port)]


def serve_experiment(experiment):
    exp_name = experiment.stem
    context = generate_experiment_context(
        Path(experiments_dir, exp_name), "/", f"/static/experiments/{exp_name}"
    )
    if web.config.get("group_index", None):
        context["group_index"] = web.config.group_index
    return render.deploy_template(**context)


class reset:
    def GET(self):
        session.kill()
        return '<html><body>Reset session, <a href="/">back to / </a></body></html>'


class serve:
    def GET(self):
        experiments = web.config.experiments
        if session.get("experiments") is None:
            session.experiments = [*experiments]
        if set(experiments) != set(session.experiments):
            session.experiments = [*experiments]
            session.incomplete = [*experiments]
        if session.get("incomplete") is None:
            session.incomplete = [*experiments]

        if len(session.incomplete) == 0:
            return render.finished()
        exp_to_serve = session.incomplete[-1]
        return serve_experiment(exp_to_serve)

    def POST(self):
        data = web.data()
        timestamp = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))

        try:
            if not session.get("incomplete"):
                if getattr(web.config, "experiments", None):
                    session.incomplete = [*web.config.experiments]
            exp_name = session.incomplete.pop() if session.get("incomplete") else Path("unknown_experiment")
        except Exception as e:
            print(f"Error accessing session data: {e}")
            exp_name = Path("unknown_experiment")

        df, exp_id = raw_to_df(data)
        cfg = web.config.run_config
        storage.save_raw(cfg, exp_id, timestamp, data)

        exp_stem = getattr(exp_name, "stem", str(exp_name))
        if should_write_bids(cfg, exp_stem):
            storage.save_bids_events(cfg, exp_id, df)

        web.header("Content-Type", "application/json")
        return "{'success': true}"


class decline:
    def GET(self):
        app.stop()


if __name__ == "__main__":
    run()
