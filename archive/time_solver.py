"\"\"\"\
Time execution tracking utilities
\"\"\"\nimport time\n\ndef time_execution(duration: float) -> None:\n    \"\"\"Time and display execution statistics\"\"\"\n    execution_time = duration\n    \n    print(f\"Execution time: {execution_time:.4f} seconds\")\n    print(f\"Execution time: {execution_time:.4f} ms\")\n"