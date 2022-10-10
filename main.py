from fastapi import FastAPI, HTTPException, status
import uvicorn
from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

app = FastAPI(
    title="OTLP backoff dependency test",
    description="OTLP backoff dependency test",
    version="0.0.1",
)

@app.get("/", responses={200: {"description": "ok"}}, include_in_schema=False)
async def root() -> None:
    """Root"""
    return status.HTTP_200_OK, "ok"

resource = Resource(
    attributes={
        SERVICE_NAME: "otlp-backoff-test",
        SERVICE_VERSION: "0.0.1",
    }
)

tracer_provider = TracerProvider(resource=resource)

processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="http://localhost:4317/v1/traces"),
)
tracer_provider.add_span_processor(processor)
trace.set_tracer_provider(tracer_provider)

metric_exporter = OTLPMetricExporter(
    endpoint="http://localhost:4317/v1/metrics"
)

meter_reader = PeriodicExportingMetricReader(
    exporter=metric_exporter,
    export_interval_millis=5000,
)

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[meter_reader],
)
metrics.set_meter_provider(meter_provider)

def main():

    uvicorn.run(
        "main:app",
    )

if __name__ == "__main__":
    main()