#!/bin/bash

# Deactivate existing venv if any
if [[ -n "$VIRTUAL_ENV" ]]; then
  echo "🔄 Deactivating existing virtualenv at $VIRTUAL_ENV"
  deactivate
fi

# Get Poetry environment path
VENV_PATH=$(poetry env info --path 2>/dev/null)

# Check if the path was found
if [ -z "$VENV_PATH" ]; then
  echo "❌ No virtual environment found. Did you run 'poetry install'?"
  return 1
fi

# Activate the environment
ACTIVATE_PATH="$VENV_PATH/bin/activate"
if [ -f "$ACTIVATE_PATH" ]; then
  echo "✅ Activating Poetry environment at $VENV_PATH"
  source "$ACTIVATE_PATH"
fi


# Export PYTHONPATH
export PYTHONPATH=.
echo "✅ PYTHONPATH set to current directory (.)"
