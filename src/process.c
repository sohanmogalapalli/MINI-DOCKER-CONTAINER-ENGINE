#include "process.h"
#include "log.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static volatile sig_atomic_t g_forward_signal = 0;
static pid_t g_child_pid = -1;

static void signal_handler(int sig) {
    g_forward_signal = sig;
    if (g_child_pid > 0) {
        kill(g_child_pid, sig);
    }
}

md_error_t process_sync_init(process_sync_t *sync) {
    if (!sync) return MD_ERR_INVALID_ARGS;

    if (pipe2(sync->sync_pipe_c2p, O_CLOEXEC) != 0) {
        md_perror("pipe2 c2p", errno);
        return MD_ERR_SYSCALL;
    }
    if (pipe2(sync->sync_pipe_p2c, O_CLOEXEC) != 0) {
        md_perror("pipe2 p2c", errno);
        close(sync->sync_pipe_c2p[0]);
        close(sync->sync_pipe_c2p[1]);
        return MD_ERR_SYSCALL;
    }

    return MD_SUCCESS;
}

void process_sync_init_in_parent(process_sync_t *sync) {
    if (!sync) return;
    /* Parent reads c2p[0] and writes p2c[1]. Close child's ends: */
    if (sync->sync_pipe_c2p[1] >= 0) { close(sync->sync_pipe_c2p[1]); sync->sync_pipe_c2p[1] = -1; }
    if (sync->sync_pipe_p2c[0] >= 0) { close(sync->sync_pipe_p2c[0]); sync->sync_pipe_p2c[0] = -1; }
}

void process_sync_init_in_child(process_sync_t *sync) {
    if (!sync) return;
    /* Child writes c2p[1] and reads p2c[0]. Close parent's ends: */
    if (sync->sync_pipe_c2p[0] >= 0) { close(sync->sync_pipe_c2p[0]); sync->sync_pipe_c2p[0] = -1; }
    if (sync->sync_pipe_p2c[1] >= 0) { close(sync->sync_pipe_p2c[1]); sync->sync_pipe_p2c[1] = -1; }
}

void process_sync_destroy(process_sync_t *sync) {
    if (!sync) return;
    if (sync->sync_pipe_c2p[0] >= 0) { close(sync->sync_pipe_c2p[0]); sync->sync_pipe_c2p[0] = -1; }
    if (sync->sync_pipe_c2p[1] >= 0) { close(sync->sync_pipe_c2p[1]); sync->sync_pipe_c2p[1] = -1; }
    if (sync->sync_pipe_p2c[0] >= 0) { close(sync->sync_pipe_p2c[0]); sync->sync_pipe_p2c[0] = -1; }
    if (sync->sync_pipe_p2c[1] >= 0) { close(sync->sync_pipe_p2c[1]); sync->sync_pipe_p2c[1] = -1; }
}

md_error_t process_sync_wait_for_parent(process_sync_t *sync) {
    if (!sync) return MD_ERR_INVALID_ARGS;

    char token = 0;
    /* Notify parent we are ready */
    if (write(sync->sync_pipe_c2p[1], "R", 1) != 1) {
        md_perror("sync write to parent", errno);
        return MD_ERR_SYSCALL;
    }

    /* Block until parent confirms setup */
    ssize_t n = read(sync->sync_pipe_p2c[0], &token, 1);
    if (n != 1 || token != 'G') {
        log_error("Child synchronization failed (parent closed or sent error)");
        return MD_ERR_SYSCALL;
    }

    return MD_SUCCESS;
}

md_error_t process_sync_notify_child(process_sync_t *sync) {
    if (!sync) return MD_ERR_INVALID_ARGS;

    char token = 0;
    /* Wait for child ready signal */
    ssize_t n = read(sync->sync_pipe_c2p[0], &token, 1);
    if (n != 1 || token != 'R') {
        log_error("Parent synchronization failed (child closed or exited prematurely)");
        return MD_ERR_SYSCALL;
    }

    /* Send GO signal to child */
    if (write(sync->sync_pipe_p2c[1], "G", 1) != 1) {
        md_perror("sync write to child", errno);
        return MD_ERR_SYSCALL;
    }

    return MD_SUCCESS;
}

md_error_t process_exec(const runtime_config_t *cfg) {
    if (!cfg || !cfg->command_argv || !cfg->command_argv[0]) {
        return MD_ERR_INVALID_ARGS;
    }

    log_debug("Executing target command: %s", cfg->command_argv[0]);
    execvp(cfg->command_argv[0], cfg->command_argv);

    int err = errno;
    md_perror("execvp", err);
    if (err == ENOENT) {
        log_error("Command '%s' not found. Ensure executable exists and PATH is valid.", cfg->command_argv[0]);
    } else if (err == EACCES) {
        log_error("Permission denied when executing '%s'", cfg->command_argv[0]);
    }

    return MD_ERR_EXEC;
}

int process_wait(pid_t pid) {
    g_child_pid = pid;

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    int status = 0;
    pid_t w;
    do {
        w = waitpid(pid, &status, 0);
    } while (w == -1 && errno == EINTR);

    g_child_pid = -1;

    if (w < 0) {
        md_perror("waitpid", errno);
        return -1;
    }

    if (WIFEXITED(status)) {
        int exit_code = WEXITSTATUS(status);
        log_debug("Child process exited normally with code %d", exit_code);
        return exit_code;
    } else if (WIFSIGNALED(status)) {
        int term_sig = WTERMSIG(status);
        log_warn("Child process terminated by signal %d (%s)", term_sig, strsignal(term_sig));
        return 128 + term_sig;
    }

    return -1;
}
