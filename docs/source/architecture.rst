Submission & moderation subsystem architecture
**********************************************

Overview
========
The submission and moderation subsystem provides:

- Accession of submission of publication content and metadata via multiple
  interfaces, including interfaces provided by trusted third-party platforms;
- Quality assurance tools and workflows to screen submissions (moderation);
- An extensible system for automating parts of the moderation process;
- An event-based log of all submission and moderation activity related
  associated with a paper.

In short, the submission and moderation subsystem is responsible for all
submission-related activities up to (but not including) publication.

Key requirements
================

1. The system must sensibly incorporate input from, and synchronize the
   activities of, a variety of human and non-human agents.
2. It must be possible for administrators to audit all changes to submission
   state in the system (e.g. by submitters, moderators, automated processes,
   etc).
3. Administrators must be able to configure automated rules and processes.
4. The system must support future development of potentially many alternative
   interfaces for submission and moderation, including interfaces developed
   and operated by trusted third-parties.
5. The system must be able to support a high volume of activity, potentially
   two orders of magnitude greater than current levels (~11k submissions per
   month in early 2018).
6. The system must make it easier to support future operational and policy
   changes around submission content, quality assurance, metadata, and other
   areas of concern.


Solution Strategy
=================

Submission system
    Refers to the collection of services/applications, data stores, and other
    components involved in the accession and moderation of new arXiv papers.
Submission
    Refers to a collection of descriptive and operational metadata, including
    a reference to a content object (e.g. a TeX source package, PDF, etc), that
    has been accessioned for possible publication in arXiv.

Separation of concerns
----------------------
In the classic arXiv submission system, there is tight coupling between the
submission and a variety of related objects and processes. For example,
processes like TeX compilation, auto-classification, etc are integrated with
web controllers for the submission UI. A major benefit of this approach is that
it keeps operations close together in the submission workflow. A major drawback
is its relative inflexibility: developing any one component of the submission
system risks generating cascading effects to other components, and assumptions
about the implementation details of components are baked into the system.

One of the major shifts in the NG reimplementation of the submission system is
to pull some of those components apart into self-contained services with
clearly-defined APIs. Our goal is to limit coupling to where it really matters,
and open the door to exchangeability of those components. This should make it
easier to develop individual components without breaking the whole system, and
also make it easier to respond to changing operational policies and procedures.

The :ref:`utility-services` section describes some of the backend components
that will be "compartmentalized" as stand-alone services in NG.

Commands (events) as data
-------------------------
The classic arXiv submission system is built around an object-centric data
model. Submissions are represented objects whose properties map to rows in a
database table, and workflows are implemented by developing web controllers
that mutate those objects (and the underlying rows). In order to support
administrative requirements of visibility onto activity in the submission
system, a log is updated by those controllers whenever they are executed.
Conditional operations are implemented by adding procedures to those
controllers. This model works well for simple systems in which there is a
single point of entry for submission data: each controller is solely
responsible for a command or set of commands, and so coupling between user
request handling/views and the commands themselves (along with conditional
operations linked to those commands) is not problematic.

A requirement of arXiv-NG is to provide consistent support for evolving and
potentially many accession pathways into arXiv. A limitation of the classic
architecture is that it requires new submission interfaces to reimplement the
commands (and rules) that it exposes, and to reimplement updates to the
administrative log. In the NG submission system, commands (and log updates)
are independent of the interface controllers -- this allows for a greater
deal of flexibility when implementing or changing interfaces. We can achieve
this either by implementing a command controller as standalone service that
handles commands from other applications, or by implementing a software package
that exposes commands as an internal API (arXiv-lib could be seen as an
attempt in that direction, although it is somewhat defeated by its broad scope
and leakage of business logic).

Another major requirement of arXiv-NG is to support triggers and automated
processes that can be configured by administrators, in addition to continuing
to support to the administrative log. A step in this direction would be to
include hooks for triggers behind the command API (above), and load parameters
(e.g. set in a database or a configuration file by an admin) that control
whether/how the trigger is executed. This has the potential to not scale well,
however, as the kinds of triggers and automation required must be anticipated
ahead of time and semi-hard-coded into the system. An alternative approach (the
one adopted here) is to define a set of primitives that explicitly represent
commands and rules, and build interfaces that allow them to be combined
arbitrarily to build workflows. In this approach, instances of command
execution (events) themselves are treated as data. This meets the requirements
of maintaining a high-fidelity comprehensive activity log.

A knock-on benefit of treating command execution/events as data is that it
allows for freer evolution of how we represent submission objects. If event
data are treated as the primary source of truth, the representation of the
submission itself can be treated as a secondary and somewhat disposable
projection. In the short term, as we reimplement components of the submission
system, we will need to guarantee that we generate projections in the classic
submission database that satisfy the requirements of legacy components that
have not yet been reimplemented. For example, when implementing a new
submission UI for NG we can collect and store new forms of data about a
submission in the event data (e.g. data used to populate new metadata fields),
but must also ensure that the appropriate tables in the classic database are
kept up-to-date for the sake of the classic moderation system. In the longer
term, projections of event data can be used to support efficient queries, but
do not constrain the evolution of the submission system in other areas.

Overview
--------
- We will decouple most functional components of the classic submission system
  into independent services that are agnostic about submissions. This includes
  classification, overlap detection, compilation (TeX, PS), and upload/file
  management.
- We will implement a :ref:`Python package <submission-core-events-package>`
  that is responsible for all commands in the scope of the submission system.
  That package should:

  - Define the commands that are available in the submission system, and
    provide a Python API for executing those commands.
  - Provide an API for defining rules and conditional operations based on those
    commands.
  - Be responsible for updating the core submission database. It should persist
    command execution instances/events in the core database, and also generate
    projections of submission state that support query/read operations and
    that are compatible with legacy components.

- A set of :ref:`core submission interface services <core-interface-services>`
  will provide UIs and APIs to support various submission and moderation
  workflows. Those services will utilize the the core command/event package
  (above).


Context
=======
Authenticated users submit new publications via a user interface. Users can
view the status of their submissions, including feedback and interventions by
moderators and administrators, and amend their submissions as necessary. They
can also view a preview of their submission, and make amendments to the source
files in their submission. Authors can supplement their published and
unpublished submissions with links to external resources and other
supplemental metadata.

Moderators (authenticated users with a moderator role) screen and curate
submissions through a moderation interface. They can generate comments, flags,
proposals, and other annotations attached to submissions.

Administrators audit and manage the submission platform, including the
behavior of automated processes and policies, through an administrative
interface. They can define rules using command/event types and conditions on
event data, and link those to other commands or processes that will execute
automatically when conditions are met.

Authors may also submit papers via authorized third-party interfaces, which
integrate with arXiv via HTTP APIs exposed by the arXiv API gateway. API
clients may deposit submissions in bulk (e.g. conference proceedings), or on
an individual basis acting directly on behalf of an arXiv user. Submissions
handled by clients operated by trusted partners may be handled differently than
submissions originating from the arXiv submission interface, as dictated by
arXiv policies.

Containers (Services & Building Blocks)
=======================================

.. _figure-submission-containers:

.. figure:: _static/diagrams/submissionContainers.png

   Containers in the arXiv submission & moderation subsystem.


.. _submission-database:

Submission database
-------------------
The submission database (currently MySQL) is responsible for the persistence of
operational and core descriptive metadata about submissions. Operational
metadata includes information related to arXiv workflows and processes. Core
descriptive metadata are the core publication metadata fields required for
arXiv submissions (e.g. title, authors, abstract). The primary source of truth
for the state of each submission is a set of transformation events. Derivative
representations (e.g. of submission objects) are also stored for querying and
rapid access.

In early phases of the classic renewal process, this will be the classic MySQL
database running in the CUL-IT datacenter. Upon migration to the cloud, this
may be replaced with something else.

.. _core-interface-services:

Core interface services
-----------------------
These services provide the core submission, moderation, and administrative
interfaces for the arXiv submission system. Each of these services integrates
with the :ref:`submission-database` to modify submission state, via the
:ref:`submission-core-events-package`.

Asynchronous operations (e.g. to execute rule-based logic) are performed by a
:ref:`submission-worker` process. Communication between the interface services
and the worker is mediated by a task queue (Redis). Tasks passed on the queue
are implemented in the :ref:`submission-core-events-package` using
`Celery <http://www.celeryproject.org/>`_.

These core interface services integrate with other services in the submission
system (e.g. :ref:`file-management-service`, :ref:`compilation-service`) via
their HTTP APIs.

.. _submission-core-events-package:

Submission core events package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This package provides an event-based Python API for CRUD operations on
submissions and submission-related (meta)data. Services (below) that operate
on submission data do so via this abstraction, which integrates with the
:ref:`submission-database`.

Rather than perform CRUD operations directly on submission objects, all
operations that modify submission data are performed through the creation of
submission events. This ensures that we have a precise and complete record of
activities concerning submissions, an explicit definition of
operations that can be performed within the arXiv submission system, and a
starting-point for building rule-based workflows to support moderation and
administrative tasks.

This package also provides integration with a Kinesis notification broker,
which propagates notifications about events in real time to other services
in the arXiv system (e.g. the :ref:`webook-notification-service`).

To support automated processes, this package also implements a set of
asynchronous tasks using `Celery <http://www.celeryproject.org/>`_. Provides
integration with a task queue (Redis) for message passing.

See :ref:`submission-core-events-package-containers`.

.. _submission-worker:

Submission worker
^^^^^^^^^^^^^^^^^
The submission worker is a Celery process that executes tasks defined in the
:ref:`submission-core-events-package` and dispatched by core interface
services. This allows us to implement rule processing asynchronously, if needed
for longer-running operations.

Submission UI service
^^^^^^^^^^^^^^^^^^^^^
Provides form-based views that allow users to create and update submissions,
and track the state of their submission through the moderation and publication
process. The interface supports metadata entry, source package upload, and
integrates with the :ref:`compilation-service` to assist the submitter in
preparing a publication-ready submission package.

Uses the :ref:`submission-core-events-package` to update submission state in
the :ref:`submission-database`.

Submission API service
^^^^^^^^^^^^^^^^^^^^^^
Provides a RESTful API for trusted clients to facilitate submission to arXiv
via external/third-party user interfaces.  Uses the
:ref:`submission-core-events-package` to update submission state in the
:ref:`submission-database`.

This will replace the existing `arXiv SWORDv1 API
<https://arxiv.org/help/submit_sword>`_.

Moderation UI service
^^^^^^^^^^^^^^^^^^^^^
Supports moderator actions on submissions. Comprised of a client-side
application (implemented in `React <https://reactjs.org/>`_) backed by a
lightweight Flask service. Uses the
:ref:`submission-core-events-package` to update submission state in the
:ref:`submission-database`.

Administrative UI service
^^^^^^^^^^^^^^^^^^^^^^^^^
The administrator interfaces provides visibility onto all parts of the
submission service, including the state and event history of all submissions
and submission annotations in the system. Administrators are able to configure
automated policies and processes, intervene on submission content and metadata,
and act on moderator proposals and comments.


.. _utility-services:

Utility services
----------------
The following utility services support the submission and moderation workflow,
providing a menu of functionality used by UI and API services to support
accession and quality assurance.

.. _file-management-service:

File management service
^^^^^^^^^^^^^^^^^^^^^^^
This service is responsible for ensuring the safety and suitability of files
uploaded to the submission system. The file management service accepts
uploads, performs verification and sanitization, and makes the upload available
for use by other services.

.. _compilation-service:

Compilation service
^^^^^^^^^^^^^^^^^^^
https://github.com/cul-it/arxiv-converter

The build service compiles sanitized upload packages into PDF, PostScript,
and other formats. This service encompasses the arXiv TeX tree. Compilation
logs are also made available, for example to provide submitters feedback about
compilation failures or warnings.

.. _plain-text-extraction-service:

Plain text extraction service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
https://github.com/cul-it/arxiv-fulltext

Extracts plain text content from PDFs, for use by the for overlap detection
and classification services. Makes both raw extracted text and normalized
"PSV" tokenized text available to other services.

.. _overlap-detection-service:

Overlap detection service
^^^^^^^^^^^^^^^^^^^^^^^^^
https://github.com/cul-it/arxiv-docsim

Operates on extracted plain text content and submission metadata to
detect possibly duplicate submissions. Returns an array of published arXiv
papers with a high degree of overlap.

.. _classifier-service:

Classifier service
^^^^^^^^^^^^^^^^^^
https://github.com/cul-it/arxiv-classifier

Operates on extracted plain text content and submission metadata to
propose categories for submitted papers.

Notification service
^^^^^^^^^^^^^^^^^^^^
Responsible for dispatching email notifications to submitters, moderators,
in response to submission system events. Provides UIs for end-user and
administrator configuration.

Endorsement service
^^^^^^^^^^^^^^^^^^^
Provides submitter endorsement mechanisms. Submission services can use the
backend API provided by this service to validate author endorsement. Provides
administrative and submitter UIs to manage endorsement status.

Web-hook notification service
-----------------------------
Provides mechanisms for API clients to register callbacks for submission
events. Event consumer is implemented using the Kinesis Consumer Library and
MultiLangDaemon [refs].