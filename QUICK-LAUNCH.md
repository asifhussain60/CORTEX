# CORTEX Documentation Quick Launch

Quick commands to launch CORTEX documentation locally.

## Launch Script

```bash
# From CORTEX project root:
./scripts/launch_docs.sh
```

This will:
1. Start HTTP server on port 8000
2. Open browser to http://localhost:8000/
3. Display URLs for easy access

## Manual Launch

```bash
# Start server only
python3 scripts/serve_docs.py 8000

# Or custom port
python3 scripts/serve_docs.py 8080
```

Then open browser to:
- **Main Site:** http://localhost:8000/
- **Story Viewer:** http://localhost:8000/story/viewer.html
- **SKULL Rulebook:** http://localhost:8000/governance/skull-rulebook.html

## macOS Alias (Terminal)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias cortex-docs='cd /Users/asifhussain/PROJECTS/CORTEX && ./scripts/launch_docs.sh'
```

Then reload shell:
```bash
source ~/.zshrc
```

Now you can launch with:
```bash
cortex-docs
```

## Stop Server

Press `Ctrl+C` in the terminal running the server.

Or find and kill the process:
```bash
lsof -ti:8000 | xargs kill
```

## Troubleshooting

### Port Already in Use
```bash
# Use different port
python3 scripts/serve_docs.py 8001
```

### Server Not Starting
```bash
# Check if port is available
lsof -i:8000

# Kill existing process
lsof -ti:8000 | xargs kill
```

### Story Not Loading
- Verify server is running: `curl http://localhost:8000/`
- Check browser console for errors
- Verify paths: `python3 docs/story/tests/test_paths.py`

## Git Pages URLs (When Published)

- **Main Site:** https://asifhussain60.github.io/CORTEX/
- **Story Viewer:** https://asifhussain60.github.io/CORTEX/story/viewer.html
- **SKULL Rulebook:** https://asifhussain60.github.io/CORTEX/governance/skull-rulebook.html
