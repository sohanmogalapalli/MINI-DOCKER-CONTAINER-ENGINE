#!/usr/bin/env python3
"""
Generate a professional PDF report and viva explanation guide for the Mini Docker project.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Suppress headers/footers on page 1 (cover)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#4A5568"))
            self.drawString(54, 750, "Mini Docker Container Engine — Project & Viva Guide")
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 750, "Operating Systems Course | VIT Vellore 2026")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

            # Footer
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 45, 558, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#718096"))
            self.drawString(54, 32, "Confidential — Academic Project Documentation")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(558, 32, page_text)
        self.restoreState()

def build_pdf(filename="MINI_DOCKER_PROJECT_AND_VIVA_GUIDE.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom palette
    NAVY = colors.HexColor("#1E3A8A")
    SLATE_DARK = colors.HexColor("#0F172A")
    TEXT_MUTED = colors.HexColor("#475569")
    BG_LIGHT = colors.HexColor("#F8FAFC")
    BORDER_COLOR = colors.HexColor("#E2E8F0")
    ACCENT_BLUE = colors.HexColor("#2563EB")
    ACCENT_GREEN = colors.HexColor("#16A34A")

    # Typography styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=NAVY,
        alignment=0,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=TEXT_MUTED,
        alignment=0,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=NAVY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SLATE_DARK,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=SLATE_DARK,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
        backColor=colors.HexColor("#F1F5F9"),
        spaceBefore=4,
        spaceAfter=6,
        leftIndent=10,
        rightIndent=10
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E3A8A")
    )

    qa_q_style = ParagraphStyle(
        'QAQuestion',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=2,
        keepWithNext=True
    )

    qa_a_style = ParagraphStyle(
        'QAAnswer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=SLATE_DARK,
        spaceAfter=8,
        leftIndent=10
    )

    story = []

    # ================= COVER PAGE =================
    story.append(Spacer(1, 20))
    story.append(Paragraph("MINI DOCKER CONTAINER ENGINE", title_style))
    story.append(Paragraph("A Lightweight Linux Container Runtime Built from Scratch in C<br/><b>Operating Systems Course Project & Comprehensive Evaluation Guide</b>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=20))

    meta_table_data = [
        [Paragraph("<b>Institution</b>", body_style), Paragraph("Vellore Institute of Technology (VIT), Vellore", body_style)],
        [Paragraph("<b>Course</b>", body_style), Paragraph("Operating Systems (OS Course Project 2026)", body_style)],
        [Paragraph("<b>Implementation Language</b>", body_style), Paragraph("C11 Standard with direct Linux/POSIX System Calls", body_style)],
        [Paragraph("<b>Target Platform</b>", body_style), Paragraph("Linux Kernel 5.8+ / WSL2 (Ubuntu Linux 6.18 x86_64)", body_style)],
        [Paragraph("<b>Key OS Primitives</b>", body_style), Paragraph("Namespaces (UTS, PID, Mount, IPC, Net), cgroup v2, chroot, pipes, waitpid", body_style)],
        [Paragraph("<b>Project Status</b>", body_style), Paragraph("<b>100% Complete & Verified</b> (All Unit & Integration Tests Passing)", body_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[160, 344])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))

    exec_summary_text = (
        "<b>Executive Summary:</b> Modern container engines (such as Docker, Podman, and runc) are often "
        "perceived by students as monolithic 'black boxes'. In reality, containers are simply ordinary Linux processes "
        "configured with kernel-enforced boundaries: <i>namespaces</i> for isolation, <i>cgroups</i> for resource limits, "
        "and <i>mount/chroot</i> for filesystem virtualization.<br/><br/>"
        "This project implements <b>Mini Docker</b>, a self-contained container runtime in C. "
        "It establishes process isolation (PID 1), hostname virtualization, mount isolation, memory limits (cgroup v2), "
        "and CPU quotas without using any container runtime libraries or external daemons."
    )
    summary_box = Table([[Paragraph(exec_summary_text, body_style)]], colWidths=[504])
    summary_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(summary_box)

    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>Table of Contents:</b>", body_bold))
    toc_data = [
        ["1. System Architecture & Component Design", "3. Step-by-Step Guide on How to Run & Test"],
        ["2. Linux Kernel Mechanisms Detailed", "4. Teacher Viva & Project Defense Guide"]
    ]
    toc_table = Table(toc_data, colWidths=[250, 254])
    toc_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0,0), (-1,-1), NAVY),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(toc_table)

    story.append(PageBreak())

    # ================= SECTION 1: ARCHITECTURE =================
    story.append(Paragraph("1. System Architecture & Engineering Design", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph(
        "Mini Docker employs a strict, layered modular architecture. Low-level kernel operations are cleanly "
        "separated from CLI argument parsing and high-level process orchestration.", body_style
    ))

    arch_table_data = [
        [Paragraph("<b>Layer / Module</b>", body_style), Paragraph("<b>Source File</b>", body_style), Paragraph("<b>Responsibilities & System Calls</b>", body_style)],
        [Paragraph("<b>CLI & Flags</b>", body_style), Paragraph("<code>src/cli.c</code>", body_style), Paragraph("Parses subcommands (<code>check</code>, <code>run</code>), separates container arguments via <code>--</code> with <code>getopt_long</code>.", body_style)],
        [Paragraph("<b>Config Validation</b>", body_style), Paragraph("<code>src/config.c</code>", body_style), Paragraph("Validates command paths, memory strings (e.g. <code>64M</code> -> bytes), CPU quota/period integers, and hostname lengths.", body_style)],
        [Paragraph("<b>Orchestrator</b>", body_style), Paragraph("<code>src/runtime.c</code>", body_style), Paragraph("Coordinates the lifecycle: environment check, process hierarchy, synchronization handshakes, and final resource cleanup.", body_style)],
        [Paragraph("<b>Namespace Engine</b>", body_style), Paragraph("<code>src/namespaces.c</code>", body_style), Paragraph("Calls <code>unshare(2)</code> with <code>CLONE_NEWUTS</code>, <code>CLONE_NEWPID</code>, <code>CLONE_NEWNS</code>, <code>CLONE_NEWIPC</code>, and <code>sethostname(2)</code>.", body_style)],
        [Paragraph("<b>Filesystem Module</b>", body_style), Paragraph("<code>src/filesystem.c</code>", body_style), Paragraph("Executes <code>mount(MS_REC|MS_PRIVATE)</code>, bind mounts rootfs, checks/mounts <code>/proc</code>, calls <code>chroot(2)</code>, and sets <code>chdir('/')</code>.", body_style)],
        [Paragraph("<b>cgroup v2 Controller</b>", body_style), Paragraph("<code>src/cgroups.c</code>", body_style), Paragraph("Manages unified cgroup v2 tree: writes <code>memory.max</code>, <code>cpu.max</code>, registers PID to <code>cgroup.procs</code>, and removes folder on exit.", body_style)],
        [Paragraph("<b>Process Supervisor</b>", body_style), Paragraph("<code>src/process.c</code>", body_style), Paragraph("Manages <code>pipe2(O_CLOEXEC)</code> synchronization, <code>execvp(2)</code> invocation, signal traps (SIGINT/SIGTERM), and <code>waitpid(2)</code> with EINTR retry.", body_style)],
    ]
    arch_table = Table(arch_table_data, colWidths=[100, 95, 309])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(arch_table)

    story.append(Paragraph("The Two-Phase PID Namespace Model", h2_style))
    story.append(Paragraph(
        "A key Operating Systems subtlety: calling <code>unshare(CLONE_NEWPID)</code> does <i>not</i> place the calling "
        "process into the new PID namespace; it only dictates that its <b>future children</b> will belong to the new namespace. "
        "To guarantee that the container process is actually <b>PID 1</b> inside its namespace, Mini Docker implements a 2-stage hierarchy:<br/>"
        "<b>1. Parent (Host)</b>: Forks Child 1 and configures cgroups.<br/>"
        "<b>2. Child 1 (Bridge Process)</b>: Calls <code>unshare(CLONE_NEWPID)</code> and immediately forks <b>Child 2</b>.<br/>"
        "<b>3. Child 2 (Container PID 1)</b>: Because it is the first child in the new namespace, <code>getpid()</code> returns <b>1</b>! "
        "Child 2 mounts rootfs and calls <code>execvp</code>.<br/>"
        "<b>4. Supervisory Wait</b>: Child 1 waits for Child 2, reaps zombie child processes, and forwards the exact exit code to Parent.",
        body_style
    ))

    story.append(Paragraph("Parent-Child Synchronization Pipe", h2_style))
    story.append(Paragraph(
        "To eliminate race conditions (such as a container executing and finishing before the host assigns its cgroup memory limit), "
        "Mini Docker uses bidirectional pipes created with <code>pipe2(O_CLOEXEC)</code>:<br/>"
        "• <i>Child</i> writes token <code>'R'</code> (Ready) and blocks.<br/>"
        "• <i>Parent</i> reads <code>'R'</code>, creates <code>/sys/fs/cgroup/mini-docker/container-PID</code>, writes limits, attaches child PID, and replies with <code>'G'</code> (Go).<br/>"
        "• <i>Child</i> receives <code>'G'</code> and executes <code>execvp</code>. The pipes auto-close on exec due to <code>O_CLOEXEC</code>.",
        body_style
    ))

    # ================= SECTION 2: KERNEL CONCEPTS =================
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Linux Kernel Mechanisms Detailed", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    concepts_data = [
        [Paragraph("<b>Kernel Primitive</b>", body_style), Paragraph("<b>How Mini Docker Implements It</b>", body_style), Paragraph("<b>OS Concept Demonstrated</b>", body_style)],
        [
            Paragraph("<b>UTS Namespace</b>", body_style),
            Paragraph("<code>unshare(CLONE_NEWUTS)</code> followed by <code>sethostname(name, len)</code>", body_style),
            Paragraph("Isolates nodename and domain name. Changing the hostname inside the container does not touch the host hostname.", body_style)
        ],
        [
            Paragraph("<b>PID Namespace</b>", body_style),
            Paragraph("<code>unshare(CLONE_NEWPID)</code> + nested <code>fork()</code>", body_style),
            Paragraph("Virtualizes process IDs. Inside the container, <code>$$ == 1</code>, enabling it to act as init and reap orphaned processes.", body_style)
        ],
        [
            Paragraph("<b>Mount Namespace & Propagation</b>", body_style),
            Paragraph("<code>unshare(CLONE_NEWNS)</code> + <code>mount(NULL, '/', NULL, MS_REC|MS_PRIVATE, NULL)</code>", body_style),
            Paragraph("Detaches mount table from host. <code>MS_PRIVATE</code> ensures bind mounts and root switches never leak to host filesystems.", body_style)
        ],
        [
            Paragraph("<b>cgroup v2 (Memory & CPU)</b>", body_style),
            Paragraph("Creates cgroup directory in unified hierarchy; writes to <code>memory.max</code>, <code>cpu.max</code>, and <code>cgroup.procs</code>", body_style),
            Paragraph("Hard resource boundaries enforced directly by Linux CFS scheduler and page reclaim subsystem. Avoids OOM affecting the host.", body_style)
        ],
        [
            Paragraph("<b>Filesystem Root (chroot)</b>", body_style),
            Paragraph("Bind mount onto itself, optional <code>/proc</code> mount, <code>chroot(path)</code>, and mandatory <code>chdir('/')</code>", body_style),
            Paragraph("Modifies the root directory pointer in process descriptor. Mandatory <code>chdir('/')</code> prevents cwd escapes.", body_style)
        ],
    ]
    concepts_table = Table(concepts_data, colWidths=[105, 175, 224])
    concepts_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(concepts_table)

    story.append(PageBreak())

    # ================= SECTION 3: HOW TO RUN =================
    story.append(Paragraph("3. Step-by-Step Guide on How to Run & Test", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph(
        "Follow these exact steps when demonstrating the project on a Linux machine or in WSL2 (Ubuntu).", body_style
    ))

    story.append(Paragraph("Step 1: Open Terminal and Verify Working Directory", h2_style))
    story.append(Paragraph("In WSL or your Linux terminal, navigate to the project directory:", body_style))
    story.append(Paragraph("<code>cd /mnt/c/Users/Sohan/Desktop/os_project</code>", code_style))

    story.append(Paragraph("Step 2: Clean and Compile the Project", h2_style))
    story.append(Paragraph(
        "The project includes a Makefile with strict C11 warning flags (<code>-Wall -Wextra -Wpedantic -Wshadow -Wconversion -Wformat=2</code>):",
        body_style
    ))
    story.append(Paragraph("<code>make clean &amp;&amp; make</code>", code_style))
    story.append(Paragraph("<i>Result: Builds <code>bin/mini-docker</code>, <code>bin/test_config</code>, and <code>bin/test_cgroups_config</code> with zero compiler warnings!</i>", body_style))

    story.append(Paragraph("Step 3: Run the Environment Check", h2_style))
    story.append(Paragraph("Inspect the host kernel, available namespaces, and cgroup v2 controllers:", body_style))
    story.append(Paragraph("<code>./bin/mini-docker check</code>", code_style))

    story.append(Paragraph("Step 4: Run the Complete Automated Test Suite", h2_style))
    story.append(Paragraph("Run the unit tests and integration tests with full verification:", body_style))
    story.append(Paragraph("<code>sudo ./scripts/run_tests.sh</code>", code_style))
    story.append(Paragraph("<i>Result: 100% of unit tests (19/19) and integration tests (6/6) pass with green output!</i>", body_style))

    story.append(Paragraph("Step 5: Run the Live Comprehensive Demo Script", h2_style))
    story.append(Paragraph("To showcase all 7 features back-to-back to the teacher:", body_style))
    story.append(Paragraph("<code>sudo ./scripts/demo.sh</code>", code_style))

    story.append(Paragraph("Step 6: Individual Demonstrations to Show Evaluators", h2_style))
    demo_cmds = [
        ("UTS Hostname Isolation", "sudo ./bin/mini-docker run --uts --hostname container-demo -- /bin/hostname", "Prints 'container-demo'. Then run 'hostname' on host to prove host is still unchanged!"),
        ("PID 1 Isolation", "sudo ./bin/mini-docker run --pid -- /bin/sh -c 'echo Inside PID is: $$'", "Outputs: 'Inside PID is: 1' proving the child process is PID 1."),
        ("Exit Code Propagation", "./bin/mini-docker run -- /bin/sh -c 'exit 42'; echo Exit code was: $?", "Outputs: 'Exit code was: 42', verifying exit status propagation."),
        ("cgroup v2 Resource Limit", "sudo ./bin/mini-docker run -v --memory 64M --cpu-quota 50000 -- /bin/echo 'Active'", "Shows verbose output: memory.max set to 67108864, cpu.max set, PID attached, and cleaned up on exit."),
        ("Filesystem (Rootfs)", "sudo ./bin/mini-docker run --rootfs ./tests/fixtures/rootfs -- /bin/init", "Outputs 'HELLO_FROM_ROOTFS', running in an isolated rootfs environment.")
    ]
    demo_table_data = [[Paragraph("<b>Feature</b>", body_style), Paragraph("<b>Command to Type</b>", body_style), Paragraph("<b>What to Point Out</b>", body_style)]]
    for feat, cmd, note in demo_cmds:
        demo_table_data.append([
            Paragraph(f"<b>{feat}</b>", body_style),
            Paragraph(f"<code>{cmd}</code>", body_style),
            Paragraph(note, body_style)
        ])
    demo_table = Table(demo_table_data, colWidths=[90, 240, 174])
    demo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(demo_table)

    story.append(PageBreak())

    # ================= SECTION 4: VIVA EXPLANATION GUIDE =================
    story.append(Paragraph("4. Teacher Viva & Project Defense Guide", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY, spaceAfter=8))

    story.append(Paragraph(
        "Below are the most critical questions professors and lab evaluators ask about container internals, "
        "along with the precise technical answers based directly on your code.", body_style
    ))

    viva_qa = [
        (
            "Q1. What is the fundamental difference between a Container and a Virtual Machine?",
            "<b>Answer:</b> A Virtual Machine (VM) runs a complete, independent guest operating system atop virtualized hardware managed by a hypervisor (e.g., KVM, VMware). This introduces high memory overhead and slower boot times.<br/>"
            "A Container is <i>not</i> a virtual machine; it is simply a standard host process that shares the host Linux kernel. The kernel restricts what the process can <i>see</i> using <b>Namespaces</b> (PID, UTS, Mount) and what it can <i>consume</i> using <b>cgroups</b>. There is zero hypervisor overhead."
        ),
        (
            "Q2. How did you make the container process run as PID 1?",
            "<b>Answer:</b> In Linux, calling <code>unshare(CLONE_NEWPID)</code> only places future children into the new PID namespace, not the calling process. "
            "To solve this, our runtime creates a bridge process (Child 1) that invokes <code>unshare(CLONE_NEWPID)</code> and then calls <code>fork()</code> to spawn Child 2. "
            "Because Child 2 is the very first process spawned in that new namespace, the Linux kernel assigns it <code>PID 1</code>. Child 1 then supervises Child 2 and propagates its exit code."
        ),
        (
            "Q3. Why isn't 'chroot' alone considered a secure container boundary?",
            "<b>Answer:</b> <code>chroot</code> only modifies the root directory pointer in the task struct. It has known escape vectors: if a process runs with root privileges (<code>CAP_SYS_CHROOT</code>), it can create a temporary subdirectory, chroot into it, and traverse out using relative paths (<code>../../</code>). "
            "Additionally, <code>chroot</code> does not isolate process tables (PIDs), hostnames (UTS), IPC queues, or resource consumption (cgroups). Real containerization requires combining Mount namespaces with <code>MS_PRIVATE</code> propagation, PID namespaces, and cgroups."
        ),
        (
            "Q4. How did you prevent race conditions between cgroup limit setup and command execution?",
            "<b>Answer:</b> If a child process is forked and immediately calls <code>execvp()</code>, a fast command could execute and terminate before the parent has finished writing limits to <code>/sys/fs/cgroup</code>. "
            "We solved this using a bidirectional synchronization pipe created with <code>pipe2(O_CLOEXEC)</code>: the child blocks waiting for a release byte (<code>'G'</code>) from the parent. Only after the parent creates the cgroup directory, writes <code>memory.max</code>, and writes the child's PID into <code>cgroup.procs</code> does it send <code>'G'</code>, releasing the child to safely execute."
        ),
        (
            "Q5. What is Mount Propagation and why did you use MS_PRIVATE?",
            "<b>Answer:</b> In systemd-based Linux systems, root mounts default to <code>MS_SHARED</code>, meaning mount or unmount events inside a mount namespace automatically replicate back to the host! "
            "In <code>src/filesystem.c</code>, we explicitly call <code>mount(NULL, '/', NULL, MS_REC | MS_PRIVATE, NULL)</code> to turn off mount propagation, guaranteeing that container mounts (like <code>/proc</code>) never leak into or alter the host system's mount table."
        ),
        (
            "Q6. How does cgroup v2 differ from legacy cgroup v1?",
            "<b>Answer:</b> cgroup v1 had separate, orthogonal hierarchies for each resource controller (e.g. <code>/sys/fs/cgroup/memory</code>, <code>/sys/fs/cgroup/cpu</code>), which caused synchronization deadlocks and broken accounting. "
            "cgroup v2 uses a single <b>unified hierarchy</b> at <code>/sys/fs/cgroup</code>. Every process belongs to exactly one cgroup, and controllers (memory, cpu, pids) are enabled hierarchically via <code>cgroup.subtree_control</code>. We use <code>memory.max</code> and <code>cpu.max</code>."
        ),
        (
            "Q7. Why did you use execvp instead of the system() library call?",
            "<b>Answer:</b> <code>system()</code> spawns an unnecessary shell (<code>/bin/sh -c ...</code>), introducing shell-injection vulnerabilities, quoting bugs, and extra process overhead. "
            "We use <code>execvp()</code> with an argument vector (<code>char **argv</code>). It replaces the current process image directly without invoking a shell, preserving spaces in arguments perfectly."
        ),
        (
            "Q8. How does Mini Docker clean up its resources after container exit?",
            "<b>Answer:</b> In <code>src/runtime.c</code> and <code>src/cgroups.c</code>, after <code>waitpid()</code> returns, the runtime immediately calls <code>cgroups_cleanup()</code>, which executes <code>rmdir()</code> on the ephemeral container cgroup directory (e.g. <code>/sys/fs/cgroup/mini-docker/container-PID</code>). We implement a retry loop with <code>usleep</code> to allow the kernel to finish draining terminated threads."
        )
    ]

    for q, a in viva_qa:
        story.append(Paragraph(q, qa_q_style))
        story.append(Paragraph(a, qa_a_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Code Walkthrough Checklist for Viva", h2_style))
    story.append(Paragraph(
        "If the professor asks to see the code, open these exact functions:<br/>"
        "• <b>Namespaces</b>: Open <code>src/namespaces.c</code> -> show <code>namespaces_apply_postfork_child()</code> where <code>unshare()</code> is called.<br/>"
        "• <b>PID 1 Logic</b>: Open <code>src/runtime.c</code> -> show <code>run_with_pid_ns()</code> where Child 1 forks Child 2.<br/>"
        "• <b>Cgroups v2</b>: Open <code>src/cgroups.c</code> -> show <code>cgroups_init_context()</code> and <code>cgroups_apply_limits()</code> writing to <code>memory.max</code>.<br/>"
        "• <b>Sync Pipe</b>: Open <code>src/process.c</code> -> show <code>process_sync_wait_for_parent()</code> and <code>process_sync_notify_child()</code>.<br/>"
        "• <b>Filesystem</b>: Open <code>src/filesystem.c</code> -> show <code>fs_setup_rootfs()</code> doing <code>mount MS_PRIVATE</code>, <code>chroot()</code>, and <code>chdir('/')</code>.",
        body_style
    ))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built: {filename}")

if __name__ == "__main__":
    output_filename = "MINI_DOCKER_PROJECT_AND_VIVA_GUIDE.pdf"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    build_pdf(output_filename)
