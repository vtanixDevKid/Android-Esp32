#!/bin/bash

termux-wake-lock
tmux new-session -d -s ai

tmux send-keys -t ai "python server.py" C-m
tmux split-window -h
tmux send-keys "python monitor.py" C-m

tmux attach -t ai