"""Tests for :mod:`events` public API."""

from unittest import TestCase, mock
import os
from collections import defaultdict
from datetime import datetime, timedelta
from flask import Flask
from .. import save, load, Submission, User, Event, \
    EventRule, RuleCondition, RuleConsequence, CreateComment, \
    SubmissionMetadata, CreateSubmission, UpdateAuthors, Author, \
    SetTitle, SetAbstract
from ..exceptions import NoSuchSubmission, InvalidEvent
from ..services import classic


def mock_store_events(*events, submission):
    """Mock for :func:`events.services.database.store_events`."""
    if submission.submission_id is None:
        submission.submission_id = 1
    for event in events:
        event.committed = True
        event.submission_id = submission.submission_id
    return submission


class TestLoad(TestCase):
    """Test :func:`.load`."""

    @mock.patch('submission.classic')
    def test_load_existant_submission(self, mock_classic):
        """When the submission exists, submission and events are returned."""
        u = User(12345, 'joe@joe.joe')
        mock_classic.get_submission.return_value = (
            Submission(creator=u, submission_id=1, owner=u,
                       created=datetime.now()),
            [CreateSubmission(creator=u, submission_id=1, committed=True)]
        )
        submission, events = load(1)
        self.assertEqual(mock_classic.get_submission.call_count, 1)
        self.assertIsInstance(submission, Submission,
                              "A submission should be returned")
        self.assertIsInstance(events, list,
                              "A list of events should be returned")
        self.assertIsInstance(events[0], Event,
                              "A list of events should be returned")

    @mock.patch('submission.classic')
    def test_load_nonexistant_submission(self, mock_classic):
        """When the submission does not exist, an exception is raised."""
        mock_classic.get_submission.side_effect = classic.NoSuchSubmission
        mock_classic.NoSuchSubmission = classic.NoSuchSubmission
        with self.assertRaises(NoSuchSubmission):
            load(1)


class TestSave(TestCase):
    """Test :func:`.save`."""

    @mock.patch('submission.classic')
    def test_save_creation_event(self, mock_database):
        """A :class:`.CreationEvent` is passed."""
        mock_database.store_events = mock_store_events
        user = User(12345, 'joe@joe.joe')
        event = CreateSubmission(creator=user)
        submission, events = save(event)
        self.assertIsInstance(submission, Submission,
                              "A submission instance should be returned")
        self.assertIsInstance(events[0], Event,
                              "Should return a list of events")
        self.assertEqual(events[0], event,
                         "The first event should be the event that was passed")
        self.assertIsNotNone(submission.submission_id,
                             "Submission ID should be set.")

    @mock.patch('submission.classic')
    def test_save_events_from_scratch(self, mock_database):
        """Save multiple events for a nonexistant submission."""
        mock_database.store_events = mock_store_events
        user = User(12345, 'joe@joe.joe')
        e = CreateSubmission(creator=user)
        e2 = SetTitle(creator=user, title='footitle')
        submission, events = save(e, e2)

        self.assertEqual(submission.metadata.title, 'footitle')
        self.assertIsInstance(submission.submission_id, int)
        self.assertEqual(submission.created, e.created)

    @mock.patch('submission.classic')
    def test_create_and_update_authors(self, mock_database):
        """Save multiple events for a nonexistant submission."""
        mock_database.store_events = mock_store_events
        user = User(12345, 'joe@joe.joe')
        e = CreateSubmission(creator=user)
        e2 = UpdateAuthors(creator=user, authors=[
            Author(0, forename='Joe', surname="Bloggs", email="joe@blog.gs")
        ])
        submission, events = save(e, e2)
        self.assertIsInstance(submission.metadata.authors[0], Author)

    @mock.patch('submission.classic')
    def test_save_from_scratch_without_creation_event(self, mock_database):
        """An exception is raised when there is no creation event."""
        mock_database.store_events = mock_store_events
        user = User(12345, 'joe@joe.joe')
        e2 = SetTitle(creator=user, title='foo')
        with self.assertRaises(NoSuchSubmission):
            save(e2)

    @mock.patch('submission.classic')
    def test_save_events_on_existing_submission(self, mock_db):
        """Save multiple sets of events in separate calls to :func:`.save`."""
        cache = defaultdict(list)

        def mock_store_events_with_cache(*events, submission):
            if submission.submission_id is None:
                submission.submission_id = 1
            for event in events:
                event.committed = True
                event.submission_id = submission.submission_id
                cache[event.submission_id].append(event)
            return submission

        def mock_get_events(submission_id):
            return cache[submission_id]

        mock_db.store_events = mock_store_events_with_cache
        mock_db.get_events = mock_get_events

        # Here is the first set of events.
        user = User(12345, 'joe@joe.joe')
        e = CreateSubmission(creator=user)
        e2 = SetTitle(creator=user, title='footitle')
        submission, _ = save(e, e2)
        submission_id = submission.submission_id

        # Now we apply a second set of events.
        e3 = SetAbstract(creator=user, abstract='bar'*10)
        submission2, _ = save(e3, submission_id=submission_id)

        # The submission state reflects all three events.
        self.assertEqual(submission2.metadata.abstract, 'bar'*10,
                         "State of the submission should reflect both sets"
                         " of events.")
        self.assertEqual(submission2.metadata.title, 'footitle',
                         "State of the submission should reflect both sets"
                         " of events.")
        self.assertEqual(submission2.created, e.created,
                         "The creation date of the submission should be the"
                         " original creation date.")
        self.assertEqual(submission2.submission_id, submission_id,
                         "The submission ID should remain the same.")