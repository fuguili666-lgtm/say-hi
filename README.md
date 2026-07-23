# Daily WeCom Greeting

This repository contains the real daily greeting task implementation. It does not call or depend on a local `launchctl` job.

## Configure

Create a local `.env` file:

```sh
cp .env.example .env
```

Then set `WECOM_WEBHOOK` to the Enterprise WeChat bot webhook URL.

## Run

Dry-run without sending:

```sh
python3 scripts/send_wecom_greeting.py --dry-run
```

Send the default greeting:

```sh
python3 scripts/send_wecom_greeting.py
```

Send custom content:

```sh
python3 scripts/send_wecom_greeting.py --message "早上好，今天也按时开始。"
```

The script can be called by any scheduler. The scheduler only needs to run this command in the repository; it should not call `launchctl kickstart` for another local task.

## Run Without This Computer

This repository includes a GitHub Actions workflow at `.github/workflows/daily-wecom-greeting.yml`.
After the repository is pushed to GitHub, GitHub can run the greeting task on its own servers, so it still runs when this computer is shut down.

Configure the repository secret:

1. Open the GitHub repository.
2. Go to `Settings` -> `Secrets and variables` -> `Actions`.
3. Add a repository secret named `WECOM_WEBHOOK`.
4. Set the value to the Enterprise WeChat bot webhook URL.

The workflow runs every day at `01:30` Asia/Shanghai time. GitHub cron expressions use UTC, so the workflow file uses `30 17 * * *`.

You can also run it manually from GitHub:

1. Open `Actions`.
2. Select `Daily WeCom Greeting`.
3. Click `Run workflow`.
