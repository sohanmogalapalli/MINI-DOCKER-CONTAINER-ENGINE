import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path):
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout

    # Color Palette definitions
    BG_DARK = RGBColor(15, 23, 42)        # Slate 900
    BG_LIGHT = RGBColor(248, 250, 252)    # Slate 50
    CARD_BG = RGBColor(255, 255, 255)     # Pure White
    CARD_BG_ALT = RGBColor(241, 245, 249) # Slate 100
    CARD_BORDER = RGBColor(226, 232, 240) # Slate 200
    
    PRIMARY_NAVY = RGBColor(30, 41, 59)   # Slate 800
    ACCENT_BLUE = RGBColor(37, 99, 235)   # Royal Blue 600
    ACCENT_CYAN = RGBColor(13, 148, 136)  # Teal 600
    ACCENT_ORANGE = RGBColor(217, 119, 6) # Amber 600
    ACCENT_GREEN = RGBColor(22, 163, 74)  # Emerald 600
    
    TEXT_MAIN = RGBColor(15, 23, 42)      # Slate 900
    TEXT_MUTED = RGBColor(71, 85, 105)    # Slate 600
    TEXT_LIGHT = RGBColor(248, 250, 252)  # Slate 50
    TEXT_DIM = RGBColor(148, 163, 184)    # Slate 400
    
    CODE_BG = RGBColor(30, 41, 59)        # Slate 800
    CODE_TEXT = RGBColor(56, 189, 248)    # Sky 400

    def add_header(slide, category, title, dark=False):
        # Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN if dark else ACCENT_BLUE

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_LIGHT if dark else PRIMARY_NAVY

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.fill.background()
        return shape

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text.strip()

    # =========================================================================
    # SLIDE 1: Title Slide (Dark Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = BG_DARK
    bg1.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.2))
    tf = tbox.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "MINI DOCKER CONTAINER ENGINE"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT
    
    p2 = tf.add_paragraph()
    p2.text = "A Lightweight Educational Container Runtime Built from Scratch Using Linux Kernel Primitives"
    p2.font.size = Pt(18)
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_before = Pt(10)

    # Info card on Title
    add_card(s1, Inches(1.0), Inches(4.0), Inches(11.3), Inches(2.7), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    info_box = s1.shapes.add_textbox(Inches(1.3), Inches(4.15), Inches(10.7), Inches(2.4))
    itf = info_box.text_frame
    itf.word_wrap = True
    
    ip1 = itf.paragraphs[0]
    ip1.text = "Operating Systems Course Project — C11 & Linux Kernel Primitives"
    ip1.font.size = Pt(15)
    ip1.font.bold = True
    ip1.font.color.rgb = TEXT_LIGHT

    ip2 = itf.add_paragraph()
    ip2.text = "• Core Mechanisms: Linux Namespaces (PID, UTS, Mount, IPC, Net) • cgroups v2 • chroot"
    ip2.font.size = Pt(12)
    ip2.font.color.rgb = TEXT_DIM
    ip2.space_before = Pt(5)

    ip3 = itf.add_paragraph()
    ip3.text = "• Team Members: Sohan (24BCE2625)  &  Rohan (24BCE2622)"
    ip3.font.size = Pt(13.5)
    ip3.font.bold = True
    ip3.font.color.rgb = RGBColor(147, 197, 253) # Light Blue
    ip3.space_before = Pt(8)

    ip4 = itf.add_paragraph()
    ip4.text = "• Course Faculty / Guide: Prof. Manivannan P"
    ip4.font.size = Pt(13.5)
    ip4.font.bold = True
    ip4.font.color.rgb = ACCENT_CYAN
    ip4.space_before = Pt(4)

    set_speaker_notes(s1, """
Respected Professor Manivannan P and evaluators, good morning/afternoon.
I am Sohan (24BCE2625), and together with my team partner Rohan (24BCE2622), we are excited to present our Operating Systems course project: 'Mini Docker' — a lightweight educational container runtime written from scratch in C11.
The goal of this project is to demystify how container platforms like Docker and Podman work under the hood. Instead of relying on pre-existing container runtimes or third-party engines, Mini Docker uses raw Linux kernel system calls — such as clone, unshare, mount, chroot, and cgroups v2 — to provide process isolation, filesystem isolation, and kernel-enforced resource control.
""")

    # =========================================================================
    # SLIDE 2: Motivation & Background: Demystifying Containers
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Motivation & Background", "Demystifying Containers: VMs vs. Containers")
    
    # Left Card: Virtual Machines
    add_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    tb_l = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    
    pl1 = tf_l.paragraphs[0]
    pl1.text = "Virtual Machines (Hypervisor-Based)"
    pl1.font.size = Pt(18)
    pl1.font.bold = True
    pl1.font.color.rgb = ACCENT_BLUE

    points_l = [
        ("Hardware Emulation:", "Requires a hypervisor (Type 1 or 2) virtualizing CPU, memory, and virtual devices."),
        ("Guest OS Overhead:", "Every VM boots a complete guest operating system kernel, consuming gigabytes of RAM."),
        ("Slow Boot Times:", "Minutes to initialize hardware, kernel, and system daemons."),
        ("Strict Isolation:", "High boundary at hardware level, but massive CPU and memory inefficiency.")
    ]
    for title, desc in points_l:
        p = tf_l.add_paragraph()
        p.text = f"• {title} {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    # Right Card: Containers (OS-Level Virtualization)
    add_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3))
    tb_r = s2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    
    pr1 = tf_r.paragraphs[0]
    pr1.text = "Containers (OS-Level Isolation)"
    pr1.font.size = Pt(18)
    pr1.font.bold = True
    pr1.font.color.rgb = ACCENT_CYAN

    points_r = [
        ("Shared Host Kernel:", "No guest kernel! Processes run directly on the host kernel via standard scheduling."),
        ("Kernel Namespaces:", "Partition kernel resources so processes only see their own isolated view (PID 1, isolated mounts)."),
        ("Control Groups (cgroups):", "Kernel throttles and caps memory usage and CPU core allocation."),
        ("Near-Zero Overhead:", "Milliseconds startup time, native C execution speed, and lightweight resource footprint.")
    ]
    for title, desc in points_r:
        p = tf_r.add_paragraph()
        p.text = f"• {title} {desc}"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(8)

    set_speaker_notes(s2, """
To understand why this project was built, we must contrast Virtual Machines with Containers.
Many developers think containers are 'lightweight VMs'. But from an Operating Systems perspective, a container is just a normal Linux process wrapped in kernel boundaries.
There is NO guest OS kernel. There is NO hypervisor.
Containers rely entirely on two OS pillars:
1. Linux Namespaces: Which govern WHAT a process can see.
2. Control Groups (cgroups): Which govern HOW MUCH resources a process can consume.
Mini Docker strips away the marketing abstractions to expose these fundamental OS concepts.
""")

    # =========================================================================
    # SLIDE 3: Problem Statement & Project Scope
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Project Definition", "Problem Statement & Engineering Scope")

    # Card 1: Problem Statement (Top)
    add_card(s3, Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.6), bg_color=CARD_BG_ALT)
    tb_p = s3.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(11.3), Inches(1.3))
    tf_p = tb_p.text_frame
    tf_p.word_wrap = True
    pp1 = tf_p.paragraphs[0]
    pp1.text = "Problem Statement"
    pp1.font.size = Pt(16)
    pp1.font.bold = True
    pp1.font.color.rgb = ACCENT_BLUE
    
    pp2 = tf_p.add_paragraph()
    pp2.text = "Applications running directly on a shared OS can interfere with one another through process table visibility, shared mount tables, global hostnames, and runaway CPU/RAM utilization. Commercial container engines (Docker, Podman) solve this but are multi-layer complex beasts (daemons, REST APIs, image registries) that obscure underlying OS primitives from computer science students."
    pp2.font.size = Pt(12)
    pp2.font.color.rgb = TEXT_MAIN
    pp2.space_before = Pt(4)

    # Card 2: What Mini Docker IS (Bottom Left)
    add_card(s3, Inches(0.8), Inches(3.4), Inches(5.6), Inches(3.5))
    tb_is = s3.shapes.add_textbox(Inches(1.0), Inches(3.55), Inches(5.2), Inches(3.2))
    tf_is = tb_is.text_frame
    tf_is.word_wrap = True
    
    pis1 = tf_is.paragraphs[0]
    pis1.text = "What Mini Docker IS"
    pis1.font.size = Pt(16)
    pis1.font.bold = True
    pis1.font.color.rgb = ACCENT_GREEN

    points_is = [
        ("Standalone C11 CLI:", "Direct interaction with POSIX and Linux system calls."),
        ("Pure OS Demonstration:", "Explicit usage of unshare, mount, chroot, and cgroup v2."),
        ("Strict Error & Signal Handling:", "EINTR retries, child sync pipes, and accurate exit status propagation."),
        ("Modular Architecture:", "Clean separation of CLI, validation, namespace, cgroup, and process lifecycles.")
    ]
    for t, d in points_is:
        p = tf_is.add_paragraph()
        p.text = f"✔ {t} {d}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(4)

    # Card 3: What Mini Docker IS NOT (Bottom Right)
    add_card(s3, Inches(6.8), Inches(3.4), Inches(5.7), Inches(3.5))
    tb_not = s3.shapes.add_textbox(Inches(7.0), Inches(3.55), Inches(5.3), Inches(3.2))
    tf_not = tb_not.text_frame
    tf_not.word_wrap = True
    
    pnot1 = tf_not.paragraphs[0]
    pnot1.text = "Academic Boundaries (What It Is NOT)"
    pnot1.font.size = Pt(16)
    pnot1.font.bold = True
    pnot1.font.color.rgb = ACCENT_ORANGE

    points_not = [
        ("No Background Daemon:", "No dockerd, socket listener, or client-server architecture."),
        ("No Image Registry Client:", "No Dockerfile parsing, layer caching, or pulling from Docker Hub."),
        ("No Multi-Tenant Sandbox Claim:", "chroot alone is not an impenetrable security jail against malicious root."),
        ("No External Dependencies:", "Zero reliance on libcontainer, runc, or third-party container libraries.")
    ]
    for t, d in points_not:
        p = tf_not.add_paragraph()
        p.text = f"✖ {t} {d}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(4)

    set_speaker_notes(s3, """
In academic software engineering, clearly defining project boundaries is vital.
Mini Docker is specifically an educational container runtime.
We do NOT claim to replace Docker daemon or pull images from Docker Hub.
Instead, we focus 100% on the core kernel mechanisms: launching an isolated process tree with its own PID namespace, UTS namespace, private mount namespace, and cgroup resource limits.
This keeps the code transparent, verifiable, and directly aligned with the OS syllabus.
""")

    # =========================================================================
    # SLIDE 4: High-Level Architecture
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "System Design", "Layered Modular Architecture")

    # 4 Architecture layer cards horizontally or stacked
    layers = [
        ("1. CLI & Input Parsing (cli.c)", "Decodes options using getopt_long; enforces '--' separator to safely separate container flags from workload arguments without shell injection.", ACCENT_BLUE),
        ("2. Configuration Validation (config.c)", "Validates byte limits (e.g., 64M, 1G), CPU quota/period integers, rootfs path existence, and sanitizes container hostnames.", PRIMARY_NAVY),
        ("3. Runtime Orchestrator (runtime.c)", "Coordinates subsystems; performs environment checks (/proc/self/ns and cgroup2 mount checks); orchestrates setup sequence.", ACCENT_CYAN),
        ("4. Low-Level Kernel Modules", "• namespaces.c: unshare() wrapper for UTS, PID, Mount, IPC, Net\n• cgroups.c: cgroup v2 filesystem writes (memory.max, cpu.max, cgroup.procs)\n• filesystem.c: MS_PRIVATE remount, bind mount, /proc mount, chroot()\n• process.c: Bidirectional sync pipes, fork(), waitpid(), signal forwarding", PRIMARY_NAVY)
    ]
    
    top_pos = 1.6
    for title, desc, col in layers:
        add_card(s4, Inches(0.8), Inches(top_pos), Inches(11.7), Inches(1.2))
        tb = s4.shapes.add_textbox(Inches(1.0), Inches(top_pos + 0.08), Inches(11.3), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MAIN
        p2.space_before = Pt(3)
        
        top_pos += 1.35

    set_speaker_notes(s4, """
Here is the high-level architecture of Mini Docker.
Notice the modular separation of concerns.
When a user runs a command:
1. `cli.c` handles argument parsing. Notice how we use the POSIX standard `--` delimiter. This prevents argument injection attacks.
2. `config.c` parses human-friendly inputs like '64M' or '50000' microseconds into validated kernel datatypes.
3. `runtime.c` coordinates all isolation primitives.
4. Finally, our low-level modules interface directly with the kernel via system calls.
This clean layering makes each component individually unit-testable.
""")

    # =========================================================================
    # SLIDE 5: Linux Namespaces Explained
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Kernel Mechanisms", "Linux Namespaces: Providing the Illusion of Isolation")

    ns_cards = [
        ("UTS Namespace", "CLONE_NEWUTS", "Isolates hostnames & NIS domain names. The container can change its hostname via sethostname() without altering the host's actual hostname.", ACCENT_BLUE),
        ("PID Namespace", "CLONE_NEWPID", "Isolates process IDs. The container target process sees itself as PID 1 (init process). It cannot see or kill host processes.", ACCENT_CYAN),
        ("Mount Namespace", "CLONE_NEWNS", "Isolates the filesystem mount table. Coupled with MS_PRIVATE, mounts and unmounts inside the container do not pollute the host OS.", ACCENT_GREEN),
        ("IPC Namespace", "CLONE_NEWIPC", "Isolates Inter-Process Communication: System V message queues, shared memory segments, and POSIX message queues.", PRIMARY_NAVY),
        ("Network Namespace", "CLONE_NEWNET", "Isolates network stack: interfaces, loopback (lo), routing tables, and firewall rules. Prevents network port conflicts.", ACCENT_ORANGE),
        ("System Call: unshare()", "unshare(flags)", "Allows a process to disassociate parts of its execution context that were previously shared with other processes, without requiring clone().", PRIMARY_NAVY)
    ]

    card_coords = [
        (Inches(0.8), Inches(1.6)), (Inches(4.8), Inches(1.6)), (Inches(8.8), Inches(1.6)),
        (Inches(0.8), Inches(4.2)), (Inches(4.8), Inches(4.2)), (Inches(8.8), Inches(4.2))
    ]

    for i, (title, flag, desc, col) in enumerate(ns_cards):
        cx, cy = card_coords[i]
        add_card(s5, cx, cy, Inches(3.7), Inches(2.4))
        tb = s5.shapes.add_textbox(cx + Inches(0.15), cy + Inches(0.15), Inches(3.4), Inches(2.1))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        
        p_flag = tf.add_paragraph()
        p_flag.text = f"Flag: {flag}"
        p_flag.font.size = Pt(10)
        p_flag.font.bold = True
        p_flag.font.color.rgb = TEXT_MUTED
        p_flag.space_before = Pt(2)
        
        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(10.5)
        p_desc.font.color.rgb = TEXT_MAIN
        p_desc.space_before = Pt(4)

    set_speaker_notes(s5, """
Linux Namespaces are the core technology behind process isolation.
A namespace wraps a global system resource in an abstraction that makes it appear to the processes within the namespace that they have their own isolated instance.
We implemented 5 major namespaces:
1. UTS: Gives the container its own hostname.
2. PID: Isolates the process ID space so the container process is PID 1.
3. Mount: Gives an independent mount table.
4. IPC: Separates shared memory and message queues.
5. Network: Separates network interfaces.
The primary system call used is `unshare()`, which detaches the calling process from its parent namespace.
""")

    # =========================================================================
    # SLIDE 6: Deep Dive: The Two-Phase PID Model
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Kernel Deep Dive", "The Two-Phase PID Namespace Model (Why PID 1 Matters)")

    # Left: Explanation Card
    add_card(s6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    tb_pid = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_pid = tb_pid.text_frame
    tf_pid.word_wrap = True

    p = tf_pid.paragraphs[0]
    p.text = "The Linux Kernel Constraint"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    points_pid = [
        ("Kernel Semantics:", "Calling unshare(CLONE_NEWPID) does NOT change the PID of the calling process! It only changes the PID namespace of SUBSEQUENT children."),
        ("The Problem:", "If the calling process executed the target program, it would still have its old PID on the host, NOT PID 1."),
        ("The Solution (Two-Phase Fork):", "We introduce a Bridge Child process. The bridge process calls unshare(CLONE_NEWPID) and then forks a second child."),
        ("The Result:", "Child 2 is born directly into the new PID namespace and receives PID 1, mimicking Linux init behavior!"),
        ("Orphan Adoption:", "In Linux, PID 1 inherits all orphaned processes inside that namespace, preventing zombie accumulation.")
    ]
    for t, d in points_pid:
        p_item = tf_pid.add_paragraph()
        p_item.text = f"• {t} {d}"
        p_item.font.size = Pt(11.5)
        p_item.font.color.rgb = TEXT_MAIN
        p_item.space_before = Pt(6)

    # Right: Flowchart / Hierarchy Card
    add_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), bg_color=CARD_BG_ALT)
    tb_flow = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_flow = tb_flow.text_frame
    tf_flow.word_wrap = True

    pf1 = tf_flow.paragraphs[0]
    pf1.text = "Process Hierarchy & Execution Flow"
    pf1.font.size = Pt(17)
    pf1.font.bold = True
    pf1.font.color.rgb = PRIMARY_NAVY

    flow_steps = [
        ("[Parent Supervisor]  (Host PID: e.g. 5420)", "• Sets up sync pipes\n• Configures cgroup v2\n• Supervises execution & traps signals", ACCENT_BLUE),
        ("   │  fork()", "", TEXT_MUTED),
        ("[Child 1: Bridge Process]  (Host PID: 5421)", "• Calls unshare(CLONE_NEWPID | CLONE_NEWUTS | ...)\n• Calls sethostname()\n• Forks target child into new PID namespace", PRIMARY_NAVY),
        ("   │  fork()", "", TEXT_MUTED),
        ("[Child 2: Workload Process]  (Namespace PID: 1)", "• getpid() == 1\n• Waits on sync pipe for cgroup setup\n• Prepares rootfs & mounts /proc\n• execvp(command_argv)", ACCENT_GREEN)
    ]
    for step_title, step_desc, col in flow_steps:
        p_step = tf_flow.add_paragraph()
        p_step.text = step_title
        p_step.font.size = Pt(12)
        p_step.font.bold = True
        p_step.font.color.rgb = col
        p_step.space_before = Pt(4)
        if step_desc:
            p_desc = tf_flow.add_paragraph()
            p_desc.text = step_desc
            p_desc.font.size = Pt(10.5)
            p_desc.font.color.rgb = TEXT_MAIN
            p_desc.space_before = Pt(2)

    set_speaker_notes(s6, """
This is one of the most critical Operating Systems concepts in our project, and a favorite question among examiners:
'Why does Mini Docker need two forks instead of one?'
According to the Linux manual for unshare: calling `unshare(CLONE_NEWPID)` does NOT change the PID of the caller. The caller remains on the host PID table. Only its subsequent children enter the new PID namespace.
Therefore, our architecture uses a two-step process:
Parent forks Child 1 (the Bridge).
Child 1 calls `unshare(CLONE_NEWPID)`.
Child 1 then forks Child 2.
Child 2 is now officially PID 1 in the new namespace! Child 2 then calls `execvp` to run the user command.
""")

    # =========================================================================
    # SLIDE 7: Resource Control: Linux cgroup v2
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Resource Control", "cgroups v2: Kernel-Enforced CPU & Memory Limits")

    # Left: Explanation Card
    add_card(s7, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    tb_cg = s7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_cg = tb_cg.text_frame
    tf_cg.word_wrap = True

    p = tf_cg.paragraphs[0]
    p.text = "Control Groups v2 (Unified Hierarchy)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    points_cg = [
        ("Why cgroups v2?", "cgroup v1 suffered from multiple conflicting hierarchies. cgroup v2 provides a unified single-root tree at /sys/fs/cgroup with consistent resource delegation."),
        ("Memory Restriction (memory.max):", "Restricts maximum RAM bytes. If the container workload exceeds this boundary, the Linux kernel Out-Of-Memory (OOM) killer is triggered on the container processes, preserving host stability."),
        ("CPU Bandwidth (cpu.max):", "Implements Completely Fair Scheduler (CFS) bandwidth control: writes 'quota period' (e.g. 50000 100000 = 50% of one CPU core)."),
        ("Process Attachment (cgroup.procs):", "Writing the container PID to cgroup.procs automatically places the entire process subtree into the restricted cgroup."),
        ("Ephemeral Lifetime & Cleanup:", "Mini Docker generates a unique per-container cgroup (/sys/fs/cgroup/mini-docker/md-XXXXXX) and automatically deletes it upon termination.")
    ]
    for t, d in points_cg:
        p_item = tf_cg.add_paragraph()
        p_item.text = f"• {t} {d}"
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = TEXT_MAIN
        p_item.space_before = Pt(5)

    # Right: Technical File Mapping Card
    add_card(s7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), bg_color=CARD_BG_ALT)
    tb_map = s7.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_map = tb_map.text_frame
    tf_map.word_wrap = True

    pm1 = tf_map.paragraphs[0]
    pm1.text = "cgroup v2 Sysfs Interface & Code Mapping"
    pm1.font.size = Pt(17)
    pm1.font.bold = True
    pm1.font.color.rgb = PRIMARY_NAVY

    cg_files = [
        ("/sys/fs/cgroup/cgroup.controllers", "Checked at startup to ensure 'memory' and 'cpu' controllers are enabled by the kernel."),
        ("cgroup.procs", "Echoes child PID: echo 5421 > md-12345/cgroup.procs.\nEnforces immediate kernel tracking."),
        ("memory.max", "Writes byte limit (e.g., 67108864 for 64M).\nMonitored via memory.current."),
        ("cpu.max", "Writes '<quota> <period>'\nQuota: 50000, Period: 100000 => Throttled to 50% CPU capacity."),
        ("cgroups_cleanup() (cgroups.c)", "Removes process from cgroup and invokes rmdir() on exit. No resource leaks!")
    ]
    for fname, fdesc in cg_files:
        pf = tf_map.add_paragraph()
        pf.text = f"📁 {fname}"
        pf.font.size = Pt(11.5)
        pf.font.bold = True
        pf.font.color.rgb = ACCENT_CYAN
        pf.space_before = Pt(5)
        
        pd = tf_map.add_paragraph()
        pd.text = fdesc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MAIN
        pd.space_before = Pt(1)

    set_speaker_notes(s7, """
Namespaces control VISIBILITY, but what prevents a rogue container from consuming 100% of host RAM and crashing the server?
That is where cgroups (Control Groups) come in.
We chose Linux cgroup v2 because it is the modern unified standard used in modern distributions.
In `cgroups.c`:
1. We probe `/sys/fs/cgroup/cgroup.controllers`.
2. We create an ephemeral sub-cgroup under `/sys/fs/cgroup/mini-docker/`.
3. We write the memory limit into `memory.max`. If the process attempts to allocate more, the kernel OOM-killer terminates it.
4. We write CPU quota and period into `cpu.max` for CFS scheduling.
5. And crucially, upon process exit, we clean up the directory with `rmdir()` so no dead cgroups linger.
""")

    # =========================================================================
    # SLIDE 8: Filesystem Isolation & chroot
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Filesystem Isolation", "Mount Namespaces, chroot, and Rootfs Preparation")

    # 3 Column Cards
    col_w = Inches(3.7)
    
    # Col 1: Mount Namespace & MS_PRIVATE
    add_card(s8, Inches(0.8), Inches(1.6), col_w, Inches(5.3))
    tb_c1 = s8.shapes.add_textbox(Inches(0.95), Inches(1.8), col_w - Inches(0.3), Inches(4.9))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    p1 = tf_c1.paragraphs[0]
    p1.text = "1. Private Mounts"
    p1.font.size = Pt(16)
    p1.font.bold = True
    p1.font.color.rgb = ACCENT_BLUE

    p1_pts = [
        "Calls unshare(CLONE_NEWNS) to detach from the host mount table.",
        "Crucial Step: Remounts root as MS_PRIVATE using:",
        "mount(NULL, '/', NULL, MS_REC | MS_PRIVATE, NULL)",
        "Why? Prevents any container mount or umount operations from propagating back to the host system!"
    ]
    for pt in p1_pts:
        p = tf_c1.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)

    # Col 2: Rootfs & chroot
    add_card(s8, Inches(4.8), Inches(1.6), col_w, Inches(5.3))
    tb_c2 = s8.shapes.add_textbox(Inches(4.95), Inches(1.8), col_w - Inches(0.3), Inches(4.9))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    p2 = tf_c2.paragraphs[0]
    p2.text = "2. chroot & chdir"
    p2.font.size = Pt(16)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_CYAN

    p2_pts = [
        "Accepts a prepared root filesystem via --rootfs (e.g. Alpine/Ubuntu rootfs).",
        "Validates rootfs path with access(R_OK | X_OK).",
        "Executes chroot(rootfs_path) to reset the logical root (/) for child process.",
        "Crucial POSIX Rule: Immediately calls chdir('/') to prevent current working directory escape vulnerability!"
    ]
    for pt in p2_pts:
        p = tf_c2.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)

    # Col 3: Virtual /proc Filesystem
    add_card(s8, Inches(8.8), Inches(1.6), col_w, Inches(5.3))
    tb_c3 = s8.shapes.add_textbox(Inches(8.95), Inches(1.8), col_w - Inches(0.3), Inches(4.9))
    tf_c3 = tb_c3.text_frame
    tf_c3.word_wrap = True
    p3 = tf_c3.paragraphs[0]
    p3.text = "3. Virtual /proc Mount"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GREEN

    p3_pts = [
        "In Linux, tools like ps, top, and kill read from /proc.",
        "Without an isolated /proc, ps inside the container would still show host processes!",
        "Mini Docker mounts a fresh proc pseudo-filesystem inside the container:",
        "mount('proc', '/proc', 'proc', MS_NOSUID|MS_NODEV|MS_NOEXEC, NULL)",
        "Now, ps inside only displays the container's PID 1 and its children!"
    ]
    for pt in p3_pts:
        p = tf_c3.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)

    set_speaker_notes(s8, """
Slide 8 focuses on filesystem isolation in `filesystem.c`.
Three essential steps occur:
First: Mount propagation. By default in systemd-based Linux distros, mounts are shared (`MS_SHARED`). We MUST explicitly remount root with `MS_PRIVATE`. Otherwise, any mount inside the container leaks to the host!
Second: `chroot`. We change the root directory to the target rootfs, and immediately do `chdir("/")`. If you don't do `chdir("/")`, a process can break out of chroot via relative paths.
Third: `/proc`. Process monitoring utilities like `ps` don't ask the kernel directly; they read `/proc`. So we mount a fresh virtual `proc` filesystem inside the container's mount namespace.
""")

    # =========================================================================
    # SLIDE 9: Process Synchronization Protocol (Pipes)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Concurrency & Synchronization", "Parent-Child Synchronization Protocol (Avoiding Race Conditions)")

    # Left: The Race Condition Problem
    add_card(s9, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    tb_rc = s9.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_rc = tb_rc.text_frame
    tf_rc.word_wrap = True

    p = tf_rc.paragraphs[0]
    p.text = "The Critical Race Condition"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ORANGE

    rc_points = [
        ("The Challenge:", "When the child process is forked, it runs concurrently with the host supervisor parent."),
        ("The Failure Mode:", "If the child immediately calls execvp(), it might execute before the parent has finished writing the child's PID into cgroup.procs and applying memory.max!"),
        ("Result of Race:", "The child process could consume unlimited host resources before constraints take effect!"),
        ("The Solution:", "A synchronous pipe barrier handshake using pipe2(O_CLOEXEC) created prior to forking.")
    ]
    for t, d in rc_points:
        p_item = tf_rc.add_paragraph()
        p_item.text = f"• {t} {d}"
        p_item.font.size = Pt(11.5)
        p_item.font.color.rgb = TEXT_MAIN
        p_item.space_before = Pt(8)

    # Right: The Handshake Sequence Diagram / Card
    add_card(s9, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), bg_color=CARD_BG_ALT)
    tb_hs = s9.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_hs = tb_hs.text_frame
    tf_hs.word_wrap = True

    phs = tf_hs.paragraphs[0]
    phs.text = "The 3-Step Handshake Protocol"
    phs.font.size = Pt(17)
    phs.font.bold = True
    phs.font.color.rgb = PRIMARY_NAVY

    hs_steps = [
        ("Step 1: Child Blocks on Pipe", "After namespaces and filesystem setup, Child 2 calls read(sync_pipe_fd, &token, 1). It pauses execution and waits for parent signal.", ACCENT_BLUE),
        ("Step 2: Parent Applies cgroups & Limits", "Parent opens /sys/fs/cgroup/mini-docker/md-XXX/cgroup.procs, writes the child PID, writes memory.max and cpu.max.", PRIMARY_NAVY),
        ("Step 3: Parent Sends 'GO' Release Token", "Parent writes token 'G' to sync_pipe. The child wakes up, closes pipe ends, and safely calls execvp(argv[0], argv).", ACCENT_GREEN),
        ("Guaranteed Security Property", "The user workload NEVER executes a single instruction without cgroup constraints already locked in place by the kernel.")
    ]
    for st, sd, sc in [(x[0], x[1], x[2]) if len(x)==3 else (x[0], x[1], PRIMARY_NAVY) for x in hs_steps]:
        p_st = tf_hs.add_paragraph()
        p_st.text = f"▶ {st}"
        p_st.font.size = Pt(12)
        p_st.font.bold = True
        p_st.font.color.rgb = sc
        p_st.space_before = Pt(6)
        
        p_sd = tf_hs.add_paragraph()
        p_sd.text = sd
        p_sd.font.size = Pt(10.5)
        p_sd.font.color.rgb = TEXT_MAIN
        p_sd.space_before = Pt(2)

    set_speaker_notes(s9, """
This slide demonstrates robust concurrent systems design in `process.c`.
In an operating systems viva, professors love to ask: 'How do you prevent race conditions between parent and child?'
If the parent and child both start running after `fork()`, who wins?
If the child runs faster, it executes the user's code BEFORE the parent can configure `memory.max` in cgroups. That would be a serious design flaw!
To solve this, Mini Docker establishes a POSIX synchronization pipe with `pipe2(O_CLOEXEC)`.
The child blocks on `read()`. The parent finishes writing the cgroup limits and writes `'G'` (Go) to the pipe.
Only then does the child awaken and call `execvp()`.
""")

    # =========================================================================
    # SLIDE 10: Signal Handling & Exit Status Propagation
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Process Supervision", "Signal Handling, EINTR Resilience, and Exit Codes")

    col_w2 = Inches(5.6)
    # Left: Signal Forwarding
    add_card(s10, Inches(0.8), Inches(1.6), col_w2, Inches(5.3))
    tb_sig = s10.shapes.add_textbox(Inches(1.0), Inches(1.8), col_w2 - Inches(0.4), Inches(4.9))
    tf_sig = tb_sig.text_frame
    tf_sig.word_wrap = True

    p = tf_sig.paragraphs[0]
    p.text = "POSIX Signal Trapping & Forwarding"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE

    sig_points = [
        ("The Issue:", "When a user presses Ctrl+C in their terminal, SIGINT is delivered to the foreground process group (the supervisor parent)."),
        ("Signal Handlers (sigaction):", "Mini Docker registers custom handlers for SIGINT, SIGTERM, and SIGHUP with SA_RESTART flag."),
        ("Forwarding to Container:", "Upon catching a signal, the supervisor immediately forwards kill(child_pid, sig) to Child 1 and Child 2."),
        ("Clean Shutdown:", "Allows container workloads to perform graceful cleanup before termination."),
        ("Cleanup Guarantee:", "Even if aborted via signal, parent's cleanup handler guarantees deletion of ephemeral cgroup folders.")
    ]
    for t, d in sig_points:
        p_item = tf_sig.add_paragraph()
        p_item.text = f"• {t} {d}"
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = TEXT_MAIN
        p_item.space_before = Pt(6)

    # Right: waitpid & Exit Code Transparency
    add_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3))
    tb_exit = s10.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_exit = tb_exit.text_frame
    tf_exit.word_wrap = True

    pe = tf_exit.paragraphs[0]
    pe.text = "EINTR Retries & Exit Code Transparency"
    pe.font.size = Pt(17)
    pe.font.bold = True
    pe.font.color.rgb = ACCENT_CYAN

    exit_points = [
        ("EINTR Loop Handling:", "waitpid() can be interrupted by arriving signals, returning -1 with errno == EINTR. Mini Docker wraps waitpid in a robust do-while loop to never drop supervision."),
        ("WIFEXITED(status):", "If child terminated normally, extracts WEXITSTATUS(status) and exits with exact same code (0 to 255)."),
        ("WIFSIGNALED(status):", "If child was killed by a fatal signal (e.g. SIGKILL), exits with standard POSIX convention: 128 + WTERMSIG(status)."),
        ("Diagnostic Logging:", "Outputs human-readable log messages indicating whether child succeeded, exited with code, or was killed by signal.")
    ]
    for t, d in exit_points:
        p_item = tf_exit.add_paragraph()
        p_item.text = f"• {t} {d}"
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = TEXT_MAIN
        p_item.space_before = Pt(6)

    set_speaker_notes(s10, """
In Slide 10, we cover process lifecycle supervision in `process.c`.
A proper container runtime must be completely transparent to the caller:
1. Signal forwarding: If the user presses Ctrl+C, the parent intercepts `SIGINT` via `sigaction` and immediately sends `kill()` down to the child container.
2. Signal interruption (`EINTR`): System calls like `waitpid` can be interrupted by signals. Without an `EINTR` loop, the supervisor would crash or return prematurely. We handle `EINTR` properly.
3. Exit Code Transparency: If the container application returns exit code 42, `mini-docker` returns exit code 42. If it was killed by `SIGKILL` (signal 9), it returns `128 + 9 = 137`.
""")

    # =========================================================================
    # SLIDE 11: CLI Interface & Feature Demonstration
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Demonstration", "Command-Line Interface & Practical Examples")

    # Command 1: Preflight check
    add_card(s11, Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.6), bg_color=CODE_BG, border_color=None)
    tb_c1 = s11.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(11.3), Inches(1.4))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    
    p = tf_c1.paragraphs[0]
    p.text = "1. Diagnostic Preflight Check (mini-docker check)"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(253, 224, 71) # Yellow
    
    p_code = tf_c1.add_paragraph()
    p_code.text = "$ ./bin/mini-docker check\n[INFO] Kernel version: Linux 6.x | Namespaces: UTS [OK] PID [OK] Mount [OK] IPC [OK] Net [OK]\n[INFO] cgroups v2 mount: /sys/fs/cgroup [MOUNTED] | Controllers: memory [OK] cpu [OK] pids [OK]"
    p_code.font.size = Pt(10)
    p_code.font.color.rgb = CODE_TEXT
    p_code.space_before = Pt(4)

    # Command 2: Hostname & PID 1 isolation
    add_card(s11, Inches(0.8), Inches(3.4), Inches(11.7), Inches(1.7), bg_color=CODE_BG, border_color=None)
    tb_c2 = s11.shapes.add_textbox(Inches(1.0), Inches(3.5), Inches(11.3), Inches(1.5))
    tf_c2 = tb_c2.text_frame
    tf_c2.word_wrap = True
    
    p = tf_c2.paragraphs[0]
    p.text = "2. UTS Hostname & PID 1 Isolation Demo"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(253, 224, 71)
    
    p_code2 = tf_c2.add_paragraph()
    p_code2.text = "$ sudo ./bin/mini-docker run --uts --hostname container-alpha --pid -- /bin/sh -c 'hostname && echo PID: $$'\ncontainer-alpha\nPID: 1\n$ hostname  # Host verification\nmy-dev-workstation  <-- HOST HOSTNAME REMAINS COMPLETELY UNTOUCHED!"
    p_code2.font.size = Pt(10)
    p_code2.font.color.rgb = CODE_TEXT
    p_code2.space_before = Pt(4)

    # Command 3: cgroup memory limit
    add_card(s11, Inches(0.8), Inches(5.3), Inches(11.7), Inches(1.7), bg_color=CODE_BG, border_color=None)
    tb_c3 = s11.shapes.add_textbox(Inches(1.0), Inches(5.4), Inches(11.3), Inches(1.5))
    tf_c3 = tb_c3.text_frame
    tf_c3.word_wrap = True
    
    p = tf_c3.paragraphs[0]
    p.text = "3. cgroup v2 Memory Limit & OOM Verification"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = RGBColor(253, 224, 71)
    
    p_code3 = tf_c3.add_paragraph()
    p_code3.text = "$ sudo ./bin/mini-docker run --memory 32M -- python3 -c 'a = [0]*100000000'\n[INFO] Initialized cgroup /sys/fs/cgroup/mini-docker/md-48192 with memory.max=33554432\n[WARN] Container process terminated by signal 9 (SIGKILL: Out Of Memory Killer)\n$ echo $? => 137  (128 + 9)"
    p_code3.font.size = Pt(10)
    p_code3.font.color.rgb = CODE_TEXT
    p_code3.space_before = Pt(4)

    set_speaker_notes(s11, """
Here we see actual terminal transcripts demonstrating Mini Docker in action:
1. `check`: Performs preflight inspection of `/proc/self/ns` and `/sys/fs/cgroup/cgroup.controllers`.
2. `run --uts --hostname ... --pid`: In one command, we set an isolated hostname and execute a shell script. The shell outputs hostname 'container-alpha' and PID '1'. Immediately after, running `hostname` on the host proves the host was unaffected.
3. Memory throttling: We launch a Python script attempting to allocate 800MB inside a 32MB cgroup limit. The Linux kernel immediately fires the OOM killer, killing the container process with signal 9, while leaving the rest of the host completely safe.
""")

    # =========================================================================
    # SLIDE 12: Verification & Testing Framework
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Verification & Quality", "Testing Strategy & Engineering Rigor")

    test_cards = [
        ("Unit Testing Suite", "make test", [
            "test_config: Validates memory parsing units (K, M, G), bounds checking, CPU quota validation.",
            "test_cgroups_config: Validates path resolution, controller string parsing, and hierarchy safety.",
            "Run automatically via Makefile test harness."
        ], ACCENT_BLUE),
        ("Compiler Hygiene", "Strict C11 Flags", [
            "-Wall -Wextra -Wpedantic: Zero tolerance for non-standard extensions.",
            "-Wshadow -Wconversion: Catches variable shadowing and signed/unsigned conversion bugs.",
            "-Wformat=2: Validates printf/snprintf formatting security."
        ], PRIMARY_NAVY),
        ("Integration Testing", "Kernel Features", [
            "Integration scripts verifying UTS isolation.",
            "PID isolation verification (checks getpid() == 1).",
            "Mount isolation verification with bind mounts.",
            "Signal propagation and exit code verification."
        ], ACCENT_GREEN)
    ]

    for i, (title, subtitle, bullets, col) in enumerate(test_cards):
        cx = Inches(0.8 + i * 4.0)
        add_card(s12, cx, Inches(1.6), Inches(3.7), Inches(5.3))
        tb = s12.shapes.add_textbox(cx + Inches(0.15), Inches(1.8), Inches(3.4), Inches(4.9))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_before = Pt(2)
        
        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(10.5)
            pb.font.color.rgb = TEXT_MAIN
            pb.space_before = Pt(8)

    set_speaker_notes(s12, """
To ensure software quality and reliability, we implemented a multi-tiered testing strategy:
1. Unit tests: Located in `tests/test_config.c` and `tests/test_cgroups_config.c`. These test our boundary conditions, memory string conversions (e.g., rejecting invalid strings or negative CPU quotas).
2. Compiler hygiene: We compiled with `-Wall -Wextra -Wpedantic -Wshadow -Wconversion` to prevent subtle bugs like integer overflows.
3. Integration testing: We verified each Linux kernel namespace feature independently to ensure no regressions.
""")

    # =========================================================================
    # SLIDE 13: Security Limitations & Real-World Comparison
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "Security Analysis", "Security Limitations & Production Runtime Comparison")

    # Left: Limitations
    add_card(s13, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3))
    tb_sec = s13.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.9))
    tf_sec = tb_sec.text_frame
    tf_sec.word_wrap = True

    p = tf_sec.paragraphs[0]
    p.text = "Educational Limitations (Not a Sandbox)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = ACCENT_ORANGE

    sec_points = [
        ("chroot is NOT an impenetrable jail:", "A process running as real root (UID 0) inside a chroot jail can easily escape by creating a temporary subdirectory and calling chroot again, or via mknod."),
        ("No Linux Capabilities Dropping:", "Full root capabilities (CAP_SYS_ADMIN, CAP_NET_ADMIN) remain available inside container unless explicitly dropped."),
        ("No Seccomp BPF Filters:", "Production engines restrict ~300 dangerous system calls via seccomp; Mini Docker permits all default system calls."),
        ("No User Namespaces (Yet):", "Root inside the container is still root on the host kernel!"),
        ("Key Lesson:", "Isolation != Full Security Sandbox. True isolation requires layered defense-in-depth.")
    ]
    for t, d in sec_points:
        p_item = tf_sec.add_paragraph()
        p_item.text = f"⚠ {t} {d}"
        p_item.font.size = Pt(11)
        p_item.font.color.rgb = TEXT_MAIN
        p_item.space_before = Pt(6)

    # Right: Comparison Table
    add_card(s13, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3))
    tb_comp = s13.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.9))
    tf_comp = tb_comp.text_frame
    tf_comp.word_wrap = True

    pc = tf_comp.paragraphs[0]
    pc.text = "Mini Docker vs. Production Docker"
    pc.font.size = Pt(17)
    pc.font.bold = True
    pc.font.color.rgb = ACCENT_BLUE

    comp_items = [
        ("Feature", "Mini Docker (Our Project)", "Docker / runc"),
        ("Architecture", "Single C executable CLI", "Client-daemon (dockerd)"),
        ("PID / UTS Namespaces", "Native unshare()", "Native clone() via runc"),
        ("Resource Throttling", "cgroup v2 (cpu, memory)", "cgroup v1 & v2 (full)"),
        ("Rootfs Switching", "chroot + chdir('/')", "pivot_root + OverlayFS"),
        ("System Call Filter", "Permissive (standard)", "Strict Seccomp BPF profiles"),
        ("Image Distribution", "Direct host directories", "OCI Images / Registries"),
        ("Privilege Dropping", "Educational (runs as root)", "Rootless & Cap dropping")
    ]
    for i, (col1, col2, col3) in enumerate(comp_items):
        p_row = tf_comp.add_paragraph()
        if i == 0:
            p_row.text = f"{col1:<16} | {col2:<18} | {col3}"
            p_row.font.bold = True
            p_row.font.size = Pt(10.5)
            p_row.font.color.rgb = PRIMARY_NAVY
        else:
            p_row.text = f"• {col1}: {col2} vs. {col3}"
            p_row.font.size = Pt(10)
            p_row.font.color.rgb = TEXT_MAIN
            p_row.space_before = Pt(3)

    set_speaker_notes(s13, """
A common question in project reviews is: 'Can I use Mini Docker to safely run untrusted malware?'
The answer is NO, and we are proud to highlight why in this slide.
`chroot` is not a complete security barrier. If a process has root privileges (UID 0), it can escape `chroot`.
Production containers like Docker and Podman use:
1. `pivot_root` instead of `chroot`
2. Seccomp BPF filters to block dangerous syscalls
3. Dropping Linux Capabilities (like `CAP_SYS_ADMIN`)
4. Layered filesystems like OverlayFS.
Acknowledging these limitations shows our deep technical understanding of operating systems security.
""")

    # =========================================================================
    # SLIDE 14: Key OS Syllabus Learning Outcomes
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "Curriculum Alignment", "Key OS Concepts & Learning Outcomes")

    outcomes = [
        ("Process Management & Lifecycle", "Practical implementation of fork(), execvp(), waitpid() with status macros (WIFEXITED, WEXITSTATUS, WTERMSIG). Understanding zombie process reaping and PID 1 responsibility.", ACCENT_BLUE),
        ("Inter-Process Communication & Concurrency", "Implementing parent-child IPC using unidirectional UNIX pipes (pipe2 with O_CLOEXEC) for barrier synchronization, preventing race conditions before execution.", ACCENT_CYAN),
        ("Memory & CPU Scheduling Controls", "Understanding CFS (Completely Fair Scheduler) quota/period mechanisms and Linux kernel page cache memory limits via the cgroup v2 sysfs virtual filesystem.", ACCENT_GREEN),
        ("Virtual Memory & Storage Virtualization", "Manipulating virtual directory trees using chroot(), mounting virtual filesystems (/proc), and configuring POSIX mount propagation flags (MS_PRIVATE).", PRIMARY_NAVY)
    ]

    top_o = 1.6
    for title, desc, col in outcomes:
        add_card(s14, Inches(0.8), Inches(top_o), Inches(11.7), Inches(1.2))
        tb = s14.shapes.add_textbox(Inches(1.0), Inches(top_o + 0.08), Inches(11.3), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MAIN
        p2.space_before = Pt(3)
        
        top_o += 1.35

    set_speaker_notes(s14, """
This slide directly maps our project to the core Operating Systems syllabus:
1. Process Lifecycle: We moved beyond textbook theory of fork and exec to real-world process management, signal trapping, and orphan adoption.
2. Concurrency & IPC: We built a real IPC pipe synchronization protocol to prevent race conditions.
3. Memory & CPU Scheduling: We interfaced directly with the kernel's memory manager and the Completely Fair Scheduler via cgroup v2.
4. Storage Virtualization: We gained hands-on experience with mount tables, mount flags, and root filesystems.
""")

    # =========================================================================
    # SLIDE 15: Viva Voce & Teacher Q&A Preparation
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "Viva Voce Guide", "Anticipated Teacher Questions & Technical Answers")

    viva_qas = [
        ("Q1: Why did you use unshare() instead of clone()?",
         "clone() requires managing raw stack allocations (void *child_stack) which varies across architectures and is error-prone in user-space. unshare() provides the exact same namespace disassociation cleanly on the current process right before a clean POSIX fork()."),
        ("Q2: Why must you mount /proc inside the container?",
         "Linux utilities (ps, top) read the /proc pseudo-filesystem to inspect process status. If /proc isn't remounted inside the container's PID/Mount namespace, ps reads the host's /proc and displays all host processes."),
        ("Q3: What happens when a container exceeds its memory limit?",
         "cgroup v2 invokes the Linux kernel Out-Of-Memory (OOM) killer. The kernel sends SIGKILL (signal 9) specifically to the rogue process inside the cgroup, cleanly stopping it while keeping host services running."),
        ("Q4: Why did you choose cgroup v2 over cgroup v1?",
         "cgroup v1 had separate trees for every controller, causing synchronization deadlocks between memory and blkio. cgroup v2 provides a unified single-root tree at /sys/fs/cgroup with safe non-root delegation.")
    ]

    top_v = 1.6
    for q, a in viva_qas:
        add_card(s15, Inches(0.8), Inches(top_v), Inches(11.7), Inches(1.2))
        tb = s15.shapes.add_textbox(Inches(1.0), Inches(top_v + 0.08), Inches(11.3), Inches(1.05))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = q
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE
        
        p2 = tf.add_paragraph()
        p2.text = f"Answer: {a}"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_MAIN
        p2.space_before = Pt(3)
        
        top_v += 1.35

    set_speaker_notes(s15, """
Here are four of the most frequent viva questions asked by evaluators:
1. 'Why unshare instead of clone?' Answer: clone requires manual assembly-level stack pointer management, whereas unshare allows standard POSIX fork/exec patterns without portability bugs.
2. 'Why mount /proc?' Answer: Because ps and top inspect /proc. Remounting /proc binds it to the container's isolated PID namespace.
3. 'What happens on memory exhaustion?' Answer: The kernel OOM killer fires SIGKILL specifically to the cgroup members.
4. 'Why cgroup v2?' Answer: It provides a unified controller hierarchy, avoiding the broken multi-hierarchy issues of v1.
""")

    # =========================================================================
    # SLIDE 16: Conclusion & Thank You (Dark Theme)
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    bg16 = s16.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg16.fill.solid()
    bg16.fill.fore_color.rgb = BG_DARK
    bg16.line.fill.background()

    # Title box
    tbox16 = s16.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(1.5))
    tf16 = tbox16.text_frame
    tf16.word_wrap = True
    p16 = tf16.paragraphs[0]
    p16.text = "CONCLUSION & SUMMARY"
    p16.font.size = Pt(34)
    p16.font.bold = True
    p16.font.color.rgb = TEXT_LIGHT

    p16_sub = tf16.add_paragraph()
    p16_sub.text = "Mini Docker: Bridging OS Theory with Practical Systems Programming"
    p16_sub.font.size = Pt(18)
    p16_sub.font.color.rgb = ACCENT_CYAN
    p16_sub.space_before = Pt(6)

    # Summary Card
    add_card(s16, Inches(1.0), Inches(2.9), Inches(11.3), Inches(3.6), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    tb_c16 = s16.shapes.add_textbox(Inches(1.3), Inches(3.1), Inches(10.7), Inches(3.2))
    tf_c16 = tb_c16.text_frame
    tf_c16.word_wrap = True

    summary_pts = [
        ("Demystified Containerization:", "Proved containers are not virtual machines, but standard Linux processes bound by kernel namespaces and cgroups."),
        ("Built in Pure C11:", "Implemented cleanly without external container engines, demonstrating direct mastery over POSIX and Linux kernel APIs."),
        ("Robust Engineering:", "Integrated pipe synchronization, signal forwarding, EINTR handling, and cgroup v2 cleanup."),
        ("Team Contribution:", "Engineered and verified by Sohan (24BCE2625) & Rohan (24BCE2622) under the guidance of Prof. Manivannan P.")
    ]
    for i, (st, sd) in enumerate(summary_pts):
        p = tf_c16.paragraphs[0] if i == 0 else tf_c16.add_paragraph()
        p.text = f"✔ {st} {sd}"
        p.font.size = Pt(13)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(8)

    p_end = tf_c16.add_paragraph()
    p_end.text = "Thank you Prof. Manivannan P! We are ready to answer your questions and demonstrate the live terminal execution."
    p_end.font.size = Pt(14)
    p_end.font.bold = True
    p_end.font.color.rgb = RGBColor(147, 197, 253)
    p_end.space_before = Pt(14)

    set_speaker_notes(s16, """
To conclude: Mini Docker has allowed us to bridge theoretical Operating Systems concepts with real-world systems programming.
We have demonstrated process isolation, filesystem isolation, resource throttling, and concurrency synchronization in pure C11.
Thank you, Professor Manivannan P, for your continuous guidance throughout this project.
Rohan and I would be glad to answer any questions and walk through the live terminal demonstration.
""")

    prs.save(output_path)
    print(f"Presentation successfully created at: {output_path}")

if __name__ == "__main__":
    out_primary = os.path.abspath("Mini_Docker_OS_Project_Presentation.pptx")
    out_alt = os.path.abspath("Mini_Docker_Presentation.pptx")
    try:
        build_presentation(out_primary)
    except PermissionError:
        print(f"[NOTE] '{out_primary}' is currently open in PowerPoint or locked. Saving to '{out_alt}' instead...")
        build_presentation(out_alt)
        print(f"To update '{out_primary}', simply close PowerPoint and run 'python generate_presentation.py'.")
