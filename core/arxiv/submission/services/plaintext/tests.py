"""Tests for :mod:`arxiv.submission.services.plaintext`."""

import io
import os
import tempfile
import time
from unittest import TestCase, mock
from threading import Thread

import docker
from flask import Flask, send_file

from arxiv.integration.api import exceptions, status
from ...tests.util import generate_token
from . import plaintext

mock_app = mock.MagicMock(config={
    'PLAINTEXT_ENDPOINT': 'http://foohost:5432',
    'PLAINTEXT_VERIFY': False
})


# class TestPlainTextService(TestCase):
#     """Tests for :class:`.plaintext.PlainTextService`."""

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_already_in_progress(self, mock_Session):
#         """A plaintext extraction is already in progress."""
#         mock_post = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.SEE_OTHER,
#                 json=mock.MagicMock(return_value={}),
#                 headers={'Location': '...'}
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(post=mock_post)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         with self.assertRaises(plaintext.ExtractionInProgress):
#             service.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction(self, mock_Session):
#         """Extraction is successfully requested."""
#         mock_session = mock.MagicMock(**{
#             'post': mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.ACCEPTED,
#                     json=mock.MagicMock(return_value={}),
#                     content='',
#                     headers={'Location': '/somewhere'}
#                 )
#             ),
#             'get': mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.OK,
#                     json=mock.MagicMock(
#                         return_value={'reason': 'extraction in process'}
#                     ),
#                     content="{'reason': 'fulltext extraction in process'}",
#                     headers={}
#                 )
#             )
#         })
#         mock_Session.return_value = mock_session
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         self.assertIsNone(service.request_extraction(source_id))
#         self.assertEqual(
#             mock_session.post.call_args[0][0],
#             'http://foohost:8123/submission/132456'
#         )

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction_bad_request(self, mock_Session):
#         """Service returns 400 Bad Request."""
#         mock_Session.return_value = mock.MagicMock(
#             post=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.BAD_REQUEST,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'something is not quite right'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.BadRequest):
#             service.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction_server_error(self, mock_Session):
#         """Service returns 500 Internal Server Error."""
#         mock_Session.return_value = mock.MagicMock(
#             post=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.INTERNAL_SERVER_ERROR,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'something is not quite right'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestFailed):
#             service.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction_unauthorized(self, mock_Session):
#         """Service returns 401 Unauthorized."""
#         mock_Session.return_value = mock.MagicMock(
#             post=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.UNAUTHORIZED,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'who are you'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestUnauthorized):
#             service.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction_forbidden(self, mock_Session):
#         """Service returns 403 Forbidden."""
#         mock_Session.return_value = mock.MagicMock(
#             post=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.FORBIDDEN,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'you do not have sufficient authz'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestForbidden):
#             service.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_is_complete(self, mock_Session):
#         """Extraction is indeed complete."""
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.SEE_OTHER,
#                 json=mock.MagicMock(return_value={}),
#                 headers={'Location': '...'}
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         self.assertTrue(service.extraction_is_complete(source_id))
#         self.assertEqual(
#             mock_get.call_args[0][0],
#             'http://foohost:8123/submission/132456/status'
#         )

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_in_progress(self, mock_Session):
#         """Extraction is still in progress."""
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.OK,
#                 json=mock.MagicMock(return_value={'status': 'in_progress'})
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         self.assertFalse(service.extraction_is_complete(source_id))
#         self.assertEqual(
#             mock_get.call_args[0][0],
#             'http://foohost:8123/submission/132456/status'
#         )

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_failed(self, mock_Session):
#         """Extraction failed."""
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.OK,
#                 json=mock.MagicMock(return_value={'status': 'failed'})
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         with self.assertRaises(plaintext.ExtractionFailed):
#             self.assertFalse(service.extraction_is_complete(source_id))

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_complete_unauthorized(self, mock_Session):
#         """Service returns 401 Unauthorized."""
#         mock_Session.return_value = mock.MagicMock(
#             get=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.UNAUTHORIZED,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'who are you'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestUnauthorized):
#             service.extraction_is_complete(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_complete_forbidden(self, mock_Session):
#         """Service returns 403 Forbidden."""
#         mock_Session.return_value = mock.MagicMock(
#             get=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.FORBIDDEN,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'you do not have sufficient authz'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestForbidden):
#             service.extraction_is_complete(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_unauthorized(self, mock_Session):
#         """Service returns 401 Unauthorized."""
#         mock_Session.return_value = mock.MagicMock(
#             get=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.UNAUTHORIZED,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'who are you'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestUnauthorized):
#             service.retrieve_content(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_forbidden(self, mock_Session):
#         """Service returns 403 Forbidden."""
#         mock_Session.return_value = mock.MagicMock(
#             get=mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.FORBIDDEN,
#                     json=mock.MagicMock(return_value={
#                         'reason': 'you do not have sufficient authz'
#                     })
#                 )
#             )
#         )
#         source_id = '132456'
#         service = plaintext.PlainTextService('foohost', 8000)
#         with self.assertRaises(exceptions.RequestForbidden):
#             service.retrieve_content(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve(self, mock_Session):
#         """Retrieval is successful."""
#         content = b'thisisthecontent'
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.OK,
#                 content=content
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         self.assertEqual(service.retrieve_content(source_id), content,
#                          "Returns binary content as received")
#         self.assertEqual(
#             mock_get.call_args[0][0],
#             'http://foohost:8123/submission/132456'
#         )

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_nonexistant(self, mock_Session):
#         """There is no such plaintext resource."""
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.NOT_FOUND,
#                 json=mock.MagicMock(return_value={'reason': 'no such thing'})
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         with self.assertRaises(exceptions.NotFound):
#             service.retrieve_content(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_in_progress(self, mock_Session):
#         """There is no such plaintext resource."""
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.SEE_OTHER,
#                 json=mock.MagicMock(return_value={}),
#                 headers={'Location': '...'}
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         service = plaintext.PlainTextService('http://foohost:8123')
#         with self.assertRaises(plaintext.ExtractionInProgress):
#             service.retrieve_content(source_id)


# class TestPlainTextServiceModule(TestCase):
#     """Tests for :mod:`.services.plaintext`."""

#     def session(self, status_code=status.OK, method="get", json={},
#                 content="", headers={}):
#         """Make a mock session."""
#         return mock.MagicMock(**{
#             method: mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status_code,
#                     json=mock.MagicMock(
#                         return_value=json
#                     ),
#                     content=content,
#                     headers=headers
#                 )
#             )
#         })

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_already_in_progress(self, mock_Session):
#         """A plaintext extraction is already in progress."""
#         mock_Session.return_value = self.session(
#             status_code=status.SEE_OTHER,
#             method='post',
#             headers={'Location': '...'}
#         )

#         source_id = '132456'
#         with self.assertRaises(plaintext.ExtractionInProgress):
#             plaintext.PlainTextService.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction(self, mock_Session):
#         """Extraction is successfully requested."""
#         mock_session = mock.MagicMock(**{
#             'post': mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.ACCEPTED,
#                     json=mock.MagicMock(return_value={}),
#                     content='',
#                     headers={'Location': '/somewhere'}
#                 )
#             ),
#             'get': mock.MagicMock(
#                 return_value=mock.MagicMock(
#                     status_code=status.OK,
#                     json=mock.MagicMock(
#                         return_value={'reason': 'extraction in process'}
#                     ),
#                     content="{'reason': 'fulltext extraction in process'}",
#                     headers={}
#                 )
#             )
#         })
#         mock_Session.return_value = mock_session
#         source_id = '132456'
#         self.assertIsNone(
#             plaintext.PlainTextService.request_extraction(source_id)
#         )
#         self.assertEqual(mock_session.post.call_args[0][0],
#                          'http://foohost:5432/submission/132456')

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_bad_request(self, mock_Session):
#         """Service returns 400 Bad Request."""
#         mock_Session.return_value = self.session(
#             status_code=status.BAD_REQUEST,
#             method='post',
#             json={'reason': 'something is not quite right'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.BadRequest):
#             plaintext.PlainTextService.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_server_error(self, mock_Session):
#         """Service returns 500 Internal Server Error."""
#         mock_Session.return_value = self.session(
#             status_code=status.INTERNAL_SERVER_ERROR,
#             method='post',
#             json={'reason': 'something is not quite right'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestFailed):
#             plaintext.PlainTextService.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_unauthorized(self, mock_Session):
#         """Service returns 401 Unauthorized."""
#         mock_Session.return_value = self.session(
#             status_code=status.UNAUTHORIZED,
#             method='post',
#             json={'reason': 'who are you'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestUnauthorized):
#             plaintext.PlainTextService.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_request_extraction_forbidden(self, mock_Session):
#         """Service returns 403 Forbidden."""
#         mock_Session.return_value = self.session(
#             status_code=status.FORBIDDEN,
#             method='post',
#             json={'reason': 'you do not have sufficient authz'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestForbidden):
#             plaintext.PlainTextService.request_extraction(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_is_complete(self, mock_Session):
#         """Extraction is indeed complete."""
#         mock_session = self.session(
#             status_code=status.SEE_OTHER,
#             headers={'Location': '...'}
#         )
#         mock_Session.return_value = mock_session
#         source_id = '132456'
#         self.assertTrue(plaintext.PlainTextService.extraction_is_complete(source_id))
#         self.assertEqual(mock_session.get.call_args[0][0],
#                          'http://foohost:5432/submission/132456/status')

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_in_progress(self, mock_Session):
#         """Extraction is still in progress."""
#         mock_session = self.session(
#             json={'status': 'in_progress'}
#         )
#         mock_Session.return_value = mock_session
#         source_id = '132456'
#         self.assertFalse(plaintext.PlainTextService.extraction_is_complete(source_id))
#         self.assertEqual(mock_session.get.call_args[0][0],
#                          'http://foohost:5432/submission/132456/status')

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_extraction_failed(self, mock_Session):
#         """Extraction failed."""
#         mock_Session.return_value = self.session(json={'status': 'failed'})
#         source_id = '132456'
#         with self.assertRaises(plaintext.ExtractionFailed):
#             self.assertFalse(plaintext.PlainTextService.extraction_is_complete(source_id))

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_complete_unauthorized(self, mock_Session):
#         """Service returns 401 Unauthorized."""
#         mock_Session.return_value = self.session(
#             status_code=status.UNAUTHORIZED,
#             json={'reason': 'who are you'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestUnauthorized):
#             plaintext.PlainTextService.extraction_is_complete(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_complete_forbidden(self, mock_Session):
#         """Service returns 403 Forbidden."""
#         mock_Session.return_value = self.session(
#             status_code=status.FORBIDDEN,
#             json={'reason': 'you do not have sufficient authz'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestForbidden):
#             plaintext.PlainTextService.extraction_is_complete(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_unauthorized(self, mock_Session):
#         """Service returns 401 Unauthorized."""
#         mock_Session.return_value = self.session(
#             status_code=status.UNAUTHORIZED,
#             json={'reason': 'who are you'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestUnauthorized):
#             plaintext.PlainTextService.retrieve_content(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_forbidden(self, mock_Session):
#         """Service returns 403 Forbidden."""
#         mock_Session.return_value = self.session(
#             status_code=status.FORBIDDEN,
#             json={'reason': 'you do not have sufficient authz'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.RequestForbidden):
#             plaintext.PlainTextService.retrieve_content(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve(self, mock_Session):
#         """Retrieval is successful."""
#         content = b'thisisthecontent'
#         mock_get = mock.MagicMock(
#             return_value=mock.MagicMock(
#                 status_code=status.OK,
#                 content=content
#             )
#         )
#         mock_Session.return_value = mock.MagicMock(get=mock_get)
#         source_id = '132456'
#         self.assertEqual(
#             plaintext.PlainTextService.retrieve_content(source_id),
#             content,
#             "Returns binary content as received"
#         )
#         self.assertEqual(mock_get.call_args[0][0],
#                          'http://foohost:5432/submission/132456')

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_nonexistant(self, mock_Session):
#         """There is no such plaintext resource."""
#         mock_Session.return_value = self.session(
#             status_code=status.NOT_FOUND,
#             json={'reason': 'no such thing'}
#         )
#         source_id = '132456'
#         with self.assertRaises(exceptions.NotFound):
#             plaintext.PlainTextService.retrieve_content(source_id)

#     @mock.patch('arxiv.integration.api.service.current_app', mock_app)
#     @mock.patch('arxiv.integration.api.service.requests.Session')
#     def test_retrieve_in_progress(self, mock_Session):
#         """There is no such plaintext resource."""
#         mock_Session.return_value = self.session(
#             status_code=status.SEE_OTHER,
#             headers={'Location': '...'}
#         )
#         source_id = '132456'
#         with self.assertRaises(plaintext.ExtractionInProgress):
#             plaintext.PlainTextService.retrieve_content(source_id)


class TestPlainTextServiceIntegration(TestCase):
    """Integration tests for the plain text service."""

    __test__  = bool(int(os.environ.get('WITH_INTEGRATION', '0')))

    @classmethod
    def setUpClass(cls):
        """Start up the plain text service."""
        client = docker.from_env()
        image = f'arxiv/{plaintext.PlainTextService.SERVICE}'
        client.images.pull(image, tag=plaintext.PlainTextService.VERSION)
        # client.images.pull('docker', tag='18-dind')
        client.images.pull('redis')

        # Create a mock preview service, from which the plaintext service
        # will retrieve a PDF.
        cls.mock_preview = Flask('preview')

        #
        @cls.mock_preview.route('/<src>/<chx>/content', methods=['GET'])
        def get_pdf(src, chx=None, fmt=None):
            response = send_file(io.BytesIO(MINIMAL_PDF.encode('utf-8')),
                                 mimetype='application/pdf')
            response.headers['ARXIV-OWNER'] = src[0]
            response.headers['ETag'] = 'footag=='
            return response

        @cls.mock_preview.route('/<src>/<chx>', methods=['HEAD'])
        @cls.mock_preview.route('/<src>/<chx>/content', methods=['HEAD'])
        def exists(src, chx=None, fmt=None):
            return '', 200, {'ARXIV-OWNER': src[0], 'ETag': 'footag=='}

        def start_preview_app():
            cls.mock_preview.run('0.0.0.0', 5009)

        t = Thread(target=start_preview_app)
        t.daemon = True
        t.start()

        cls.network = client.networks.create('test-plaintext-network')
        cls.data = client.volumes.create(name='data', driver='local')

        # This is the volume shared by the worker and the docker host.
        cls.pdfs = tempfile.mkdtemp()

        cls.plaintext_api = client.containers.run(
            f'{image}:{plaintext.PlainTextService.VERSION}',
            detach=True,
            network='test-plaintext-network',
            ports={'8000/tcp': 8889},
            name='plaintext',
            volumes={'data': {'bind': '/data', 'mode': 'rw'},
                     cls.pdfs: {'bind': '/pdfs', 'mode': 'rw'}},
            environment={
                'NAMESPACE': 'test',
                'REDIS_ENDPOINT': 'test-plaintext-redis:6379',
                'PREVIEW_ENDPOINT': 'http://host.docker.internal:5009',
                'JWT_SECRET': 'foosecret',
                'MOUNTDIR': cls.pdfs
            },
            command=["uwsgi", "--ini", "/opt/arxiv/uwsgi.ini"]
        )
        cls.redis = client.containers.run(
            f'redis',
            detach=True,
            network='test-plaintext-network',
            name='test-plaintext-redis'
        )
        cls.plaintext_worker = client.containers.run(
            f'{image}:{plaintext.PlainTextService.VERSION}',
            detach=True,
            network='test-plaintext-network',
            volumes={'data': {'bind': '/data', 'mode': 'rw'},
                     cls.pdfs: {'bind': '/pdfs', 'mode': 'rw'},
                     '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}},
            environment={
                'NAMESPACE': 'test',
                'REDIS_ENDPOINT': 'test-plaintext-redis:6379',
                'DOCKER_HOST': 'unix://var/run/docker.sock',
                'PREVIEW_ENDPOINT': 'http://host.docker.internal:5009',
                'JWT_SECRET': 'foosecret',
                'MOUNTDIR': cls.pdfs
            },
            command=["celery", "worker", "-A", "fulltext.worker.celery_app",
                     "--loglevel=INFO", "-E", "--concurrency=1"]
        )
        time.sleep(5)

        cls.app = Flask('test')
        cls.app.config.update({
            'PLAINTEXT_SERVICE_HOST': 'localhost',
            'PLAINTEXT_SERVICE_PORT': '8889',
            'PLAINTEXT_PORT_8889_PROTO': 'http',
            'PLAINTEXT_VERIFY': False,
            'PLAINTEXT_ENDPOINT': 'http://localhost:8889',
            'JWT_SECRET': 'foosecret'
        })
        cls.token = generate_token(cls.app, ['fulltext:create', 'fulltext:read'])
        plaintext.PlainTextService.init_app(cls.app)

    @classmethod
    def tearDownClass(cls):
        """Tear down the plain text service."""
        cls.plaintext_api.kill()
        cls.plaintext_api.remove()
        cls.plaintext_worker.kill()
        cls.plaintext_worker.remove()
        cls.redis.kill()
        cls.redis.remove()
        cls.data.remove()
        cls.network.remove()

    def test_get_status(self):
        """Get the status endpoint."""
        with self.app.app_context():
            pt = plaintext.PlainTextService.current_session()
            self.assertEqual(pt.get_status(),
                             {'extractor': True, 'storage': True})

    def test_is_available(self):
        """Poll for availability."""
        with self.app.app_context():
            pt = plaintext.PlainTextService.current_session()
            self.assertTrue(pt.is_available())

    def test_extraction(self):
        """Request, poll, and retrieve a plain text extraction."""
        with self.app.app_context():
            pt = plaintext.PlainTextService.current_session()
            self.assertIsNone(
                pt.request_extraction('1234', 'foochex', self.token)
            )
            tries = 0
            while not pt.extraction_is_complete('1234', 'foochex', self.token):
                print('waiting for extraction to complete:', tries)
                tries += 1
                time.sleep(5)
                if tries > 20:
                    self.fail('waited too long')
            print('done')
            content = pt.retrieve_content('1234', 'foochex', self.token)
            self.assertEqual(content.read().strip(), b'Hello World')


# From https://brendanzagaeski.appspot.com/0004.html
MINIMAL_PDF = """
%PDF-1.1
%¥±ë

1 0 obj
  << /Type /Catalog
     /Pages 2 0 R
  >>
endobj

2 0 obj
  << /Type /Pages
     /Kids [3 0 R]
     /Count 1
     /MediaBox [0 0 300 144]
  >>
endobj

3 0 obj
  <<  /Type /Page
      /Parent 2 0 R
      /Resources
       << /Font
           << /F1
               << /Type /Font
                  /Subtype /Type1
                  /BaseFont /Times-Roman
               >>
           >>
       >>
      /Contents 4 0 R
  >>
endobj

4 0 obj
  << /Length 55 >>
stream
  BT
    /F1 18 Tf
    0 0 Td
    (Hello World) Tj
  ET
endstream
endobj

xref
0 5
0000000000 65535 f
0000000018 00000 n
0000000077 00000 n
0000000178 00000 n
0000000457 00000 n
trailer
  <<  /Root 1 0 R
      /Size 5
  >>
startxref
565
%%EOF
"""