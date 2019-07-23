Submission & announcement process
*********************************

This section describes the classic arXiv submission and announcement process at
a high level.

Submissions & states
--------------------
An arXiv submission is comprised of a source package and a collection of
procedural and descriptive metadata. The source package is usually comprised of
a scientific paper (generally in LaTeX) and auxiliary resources (e.g. images,
tables, errata); see :ref:`supported-source-formats`.

The primary objectives of the arXiv submission system are rapid dissemination
of scientific findings, and to support QA/QC workflows for arXiv's volunteer
moderators and the operations team. For a glimpse into how arXiv submissions
are processed on a daily basis, see `this recent blog post
<https://blogs.cornell.edu/arxiv/2018/01/19/a-day-in-the-life-of-the-arxiv-admin-team/>`_.

In support of rapid dissemination, a core requirement for the submission
system is that the daily announcement process should continue
even in the absence of human intervention. In other words, if the moderation
and operations teams were disbanded tomorrow, arXiv would continue to accept
and disseminate e-prints as usual.

At any given time, a submission will be in one of the states described below.

.. note::

   It should be noted that in the arXiv-NG submission system these states are
   defined in terms of the the data that describes the submission, **not** by a
   flag in the database.


.. _figure-submission-states:

.. figure:: _static/diagrams/submissionState.png

   State transitions for arXiv submissions.


Working
    When the submission process is initiated, it generally lacks some of the
    (meta)data and/or content required for announcement. For example, the
    submission process may be initiated by sending preliminary information for
    only a few metadata fields, leaving the submission source package to be
    uploaded separately. Several users and/or API clients may be involved in
    contributing information about the submission. The source package must
    compile to a usable PDF before a submission can leave the working
    state.

Processing
    Once a submission is finalized (ready for announcement), it is subject to
    a handful of automated QA/QC checks. For example, we need to be able to
    extract plain text content from the compiled paper for subsequent checks.
    Depending on the results of those checks, the submission may be bounced
    back to the working state to correct problems. Generally, a submission
    remains in the processing state for a very short period of time (seconds or
    minutes).

Submitted
    If the preliminary checks pass, the submission is considered to be in the
    submitted state. Automated checks for technical issues may also be applied
    while the submission is in this state, and members of the moderation and
    operations teams may inspect the paper for quality or to address issues
    flagged by the technical checks. If a moderation flag is applied to the
    submission during this process, the submission transitions to the **On
    Hold** state (below). If no moderation or administrative flags are raised
    on the submission, the submission will automatically transition to the
    **Scheduled** state (below) at one of two cutoff times.

On Hold
    A submission in this state has been flagged by a moderator or by an
    automated QA/QC process for potential problems. Submissions in this state
    are usually inspected by the operations team, who may reach out to the
    submission owner. If and when the issues with the submission are resolved,
    an administrator will remove the blocking flags from the submission, and
    the submission will return to the **Submitted** state.

Scheduled
    Any submissions in the **Submitted** state at the announcement cut-off time
    (currently 2PM ET) will be automatically scheduled for announcement on the
    same day (currently 8PM ET). Any remaining submissions in the **Submitted**
    state at the next-day cutoff (currently 8PM ET) will be scheduled for
    announcement on the following day.

Announced
    The automated announcement process runs daily, currently at 8PM ET. Any
    submissions scheduled for the current day will be updated with their
    arXiv ID and version, and an announcement timestamp. At that time, the
    submission is considered **Announced**. No further changes
    may be made to a submission in this state.
