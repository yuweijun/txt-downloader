# PM2 Commands for txt-downloader

## Start the application
```bash
pm2 start ecosystem.config.js
# or
./start.sh
```

## Stop the application
```bash
pm2 stop txt-downloader
```

## Restart the application
```bash
pm2 restart txt-downloader
```

## Delete from PM2
```bash
pm2 delete txt-downloader
```

## View logs
```bash
# Real-time logs
pm2 logs txt-downloader

# Last 100 lines
pm2 logs txt-downloader --lines 100

# Only errors
pm2 logs txt-downloader --err

# Clear logs
pm2 flush txt-downloader
```

## Monitor status
```bash
# List all apps
pm2 list

# Detailed info
pm2 show txt-downloader

# Monitor CPU/Memory
pm2 monit
```

## Development mode
```bash
# Start with development environment
pm2 start ecosystem.config.js --env development

# Watch files for auto-restart
pm2 start ecosystem.config.js --watch
```

## Save PM2 configuration
```bash
# Save current PM2 process list
pm2 save

# Setup PM2 to start on system boot
pm2 startup
```

## Useful commands
```bash
# Reload (graceful restart)
pm2 reload txt-downloader

# Stop all apps
pm2 stop all

# Restart all apps
pm2 restart all

# Delete all apps
pm2 delete all
```
