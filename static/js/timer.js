/**
 * StudyPlanner Timer Controller
 * Handles study stopwatch ticking, AJAX communication with /timer/start and /timer/stop endpoints.
 */

class StudyTimer {
    constructor() {
        this.btnStart = document.getElementById('btn-start-timer');
        this.btnStop = document.getElementById('btn-stop-timer');
        this.clockDisplay = document.getElementById('timer-clock');
        this.statusText = document.getElementById('timer-status-text');
        this.currentSessionDisplay = document.getElementById('current-session-time');
        this.totalTimeDisplay = document.getElementById('total-task-time');
        this.statusBadge = document.getElementById('task-status-badge');

        this.elapsedSeconds = 0;
        this.timerInterval = null;
        this.isRunning = false;

        if (this.btnStart && this.btnStop) {
            this.taskId = this.btnStart.getAttribute('data-task-id');
            this.bindEvents();
        }
    }

    bindEvents() {
        this.btnStart.addEventListener('click', () => this.startTimer());
        this.btnStop.addEventListener('click', () => this.stopTimer());
    }

    startTimer() {
        if (this.isRunning) return;

        const csrfToken = getCsrfToken();
        fetch(`/task/${this.taskId}/timer/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                this.isRunning = true;
                this.btnStart.disabled = true;
                this.btnStop.disabled = false;
                this.statusText.textContent = 'Focusing... Session Active';
                this.statusText.style.color = 'var(--success-color)';

                if (this.statusBadge) {
                    this.statusBadge.textContent = 'In Progress';
                    this.statusBadge.className = 'badge badge-info';
                }

                this.timerInterval = setInterval(() => {
                    this.elapsedSeconds++;
                    this.updateDisplay();
                }, 1000);
            } else {
                alert('Error starting timer: ' + (data.error || 'Unknown error'));
            }
        })
        .catch((err) => {
            console.error('Failed to start timer session:', err);
            alert('Failed to connect to study timer service.');
        });
    }

    stopTimer() {
        if (!this.isRunning) return;

        const csrfToken = getCsrfToken();
        fetch(`/task/${this.taskId}/timer/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                clearInterval(this.timerInterval);
                this.isRunning = false;
                this.btnStart.disabled = false;
                this.btnStop.disabled = true;
                this.statusText.textContent = `Session Saved (+${data.duration}s)`;
                this.statusText.style.color = 'var(--primary-color)';

                if (data.formatted_duration && this.totalTimeDisplay) {
                    this.totalTimeDisplay.textContent = data.formatted_duration;
                }

                // Reset local session clock after saving
                this.elapsedSeconds = 0;
                this.updateDisplay();
            } else {
                alert('Error stopping timer: ' + (data.error || 'Unknown error'));
            }
        })
        .catch((err) => {
            console.error('Failed to stop timer session:', err);
            alert('Failed to record session.');
        });
    }

    updateDisplay() {
        const formatted = this.formatSeconds(this.elapsedSeconds);
        if (this.clockDisplay) {
            this.clockDisplay.textContent = formatted;
        }
        if (this.currentSessionDisplay) {
            this.currentSessionDisplay.textContent = formatted;
        }
    }

    formatSeconds(totalSecs) {
        const hrs = Math.floor(totalSecs / 3600);
        const mins = Math.floor((totalSecs % 3600) / 60);
        const secs = totalSecs % 60;
        return [hrs, mins, secs]
            .map((v) => (v < 10 ? '0' + v : v))
            .join(':');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new StudyTimer();
});
