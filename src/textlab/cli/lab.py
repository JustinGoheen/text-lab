import os
from pathlib import Path

import typer
from pytorch_lightning.callbacks import EarlyStopping
from pytorch_lightning.loggers.csv_logs import CSVLogger
from pytorch_lightning.loggers.wandb import WandbLogger
from pytorch_lightning.profilers import PyTorchProfiler
from typing_extensions import Annotated

from textlab import Config, LabDataModule, LabModule, LabTrainer

FILEPATH = Path(__file__)
PROJECTPATH = FILEPATH.parents[2]
PKGPATH = FILEPATH.parents[1]

app = typer.Typer()
docs_app = typer.Typer()
run_app = typer.Typer()
app.add_typer(docs_app, name="docs")
app.add_typer(run_app, name="run")


@app.callback()
def callback() -> None:
    pass


# Docs


@docs_app.command("build")
def build_docs() -> None:
    import shutil

    os.system("mkdocs build")
    shutil.copyfile(src="README.md", dst="docs/index.md")


@docs_app.command("serve")
def serve_docs() -> None:
    os.system("mkdocs serve")


# Run


@run_app.command("dev-run")
def run_dev_run():
    datamodule = LabDataModule()
    model = LabModule()
    trainer = LabTrainer(fast_dev_run=True)
    trainer.fit(model=model, datamodule=datamodule)


@run_app.command("demo-run")
def run_demo_run(
    logger: Annotated[str, typer.Option(help="logger to use. one of (`wandb`, `csv`)")] = "csv",
):
    if logger == "wandb":
        logger = WandbLogger(name="textlab-demo", save_dir=Config.WANDBPATH, project=Config.PROJECTNAME)

    else:
        logger = CSVLogger(save_dir=Config.CSVLOGGERPATH)

    datamodule = LabDataModule()
    model = LabModule()
    trainer = LabTrainer(
        devices="auto",
        accelerator="auto",
        strategy="auto",
        num_nodes=1,
        precision="32-true",
        enable_checkpointing=True,
        max_epochs=2,
        callbacks=EarlyStopping(monitor="val-loss", mode="min"),
        logger=logger,
        profiler=PyTorchProfiler(dirpath="logs/torch_profiler"),
    )
    trainer.fit(model=model, datamodule=datamodule)


@run_app.command("streamlit")
def run_streamlit():
    os.system(f"streamlit run {PKGPATH / 'app/streamlit.py'}")
