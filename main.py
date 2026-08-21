from pathlib import Path

from src.common.config import AppConfig
from src.pipeline.orchestrator import CVParserPipeline


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    config = AppConfig(input_dir=project_root / "cvs", output_dir=project_root / "output")
    pipeline = CVParserPipeline(config)
    results = pipeline.run()
    print(f"Processed {len(results)} CV(s). Results saved to {config.output_dir}")
