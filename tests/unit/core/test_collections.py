import mock
import os

from boto3.core.connection import ConnectionFactory
from boto3.core.exceptions import APIVersionMismatchError
from boto3.core.collections import ResourceJSONLoader, CollectionDetails
from boto3.core.collections import Collection, CollectionFactory
from boto3.core.session import Session

from tests import unittest
from tests.unit.fakes import FakeParam, FakeOperation, FakeService, FakeSession


class TestCoreService(FakeService):
    api_version = '2013-08-23'
    operations = [
        FakeOperation(
            'CreateQueue',
            " <p>Creates a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
                FakeParam('Attributes', required=False, ptype='map'),
            ],
            output={
                'shape_name': 'CreateQueueResult',
                'type': 'structure',
                'members': {
                    'QueueUrl': {
                        'shape_name': 'String',
                        'type': 'string',
                        'documentation': '\n    <p>The URL for the created SQS queue.</p>\n  ',
                    },
                },
            },
            result=(None, {
                'QueueUrl': 'http://example.com',
            })
        ),
        FakeOperation(
            'SendMessage',
            " <p>Sends a message to a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
                FakeParam('MessageBody', required=True, ptype='string'),
                FakeParam('MessageType', required=False, ptype='string'),
            ],
            output=True,
            result=(None, True)
        ),
        FakeOperation(
            'ReceiveMessage',
            " something something something ",
            params=[
                FakeParam('QueueUrl', required=True, ptype='string'),
                FakeParam('AttributeNames', required=False, ptype='list'),
                FakeParam('MaxNumberOfMessages', required=False, ptype='integer'),
                FakeParam('VisibilityTimeout', required=False, ptype='integer'),
                FakeParam('WaitTimeSeconds', required=False, ptype='integer'),
            ],
            output={
                'shape_name': 'ReceiveMessageResult',
                'type': 'structure',
                'members': {
                    'Messages': {
                        'shape_name': 'MessageList',
                        'type': 'list',
                        'members': {
                            'shape_name': 'Message',
                            'type': 'structure',
                            'members': {
                                'MessageId': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'ReceiptHandle': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'MD5OfBody': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'Body': {
                                    'shape_name': 'String',
                                    'type': 'string',
                                    'documentation': None
                                },
                                'Attributes': {
                                    'shape_name': 'AttributeMap',
                                    'type': 'map',
                                    'keys': {
                                        'shape_name': 'QueueAttributeName',
                                        'type': 'string',
                                        'enum': [
                                            'Policy',
                                            'VisibilityTimeout',
                                            'MaximumMessageSize',
                                            'MessageRetentionPeriod',
                                            'ApproximateNumberOfMessages',
                                            'ApproximateNumberOfMessagesNotVisible',
                                            'CreatedTimestamp',
                                            'LastModifiedTimestamp',
                                            'QueueArn',
                                            'ApproximateNumberOfMessagesDelayed',
                                            'DelaySeconds',
                                            'ReceiveMessageWaitTimeSeconds'
                                        ],
                                        'documentation': '\n    <p>The name of a queue attribute.</p>\n  ',
                                        'xmlname': 'Name'
                                    },
                                    'members': {
                                        'shape_name': 'String',
                                        'type': 'string',
                                        'documentation': '\n    <p>The value of a queue attribute.</p>\n  ',
                                        'xmlname': 'Value'
                                    },
                                    'flattened': True,
                                    'xmlname': 'Attribute',
                                    'documentation': None,
                                },
                            },
                            'documentation': None,
                            'xmlname': 'Message'
                        },
                        'flattened': True,
                        'documentation': '\n    <p>A list of messages.</p>\n  '
                    }
                },
                'documentation': None
            },
            result=(None, {
                'Messages': [
                    {
                        'MessageId': 'msg-12345',
                        'ReceiptHandle': 'hndl-12345',
                        'MD5OfBody': '6cd3556deb0da54bca060b4c39479839',
                        'Body': 'Hello, world!',
                        'Attributes': {
                            'QueueArn': 'arn:aws:example:example:sqs:something',
                            'ApproximateNumberOfMessagesDelayed': '2',
                            'DelaySeconds': '10',
                            'CreatedTimestamp': '2013-10-17T21:52:46Z',
                            'LastModifiedTimestamp': '2013-10-17T21:52:46Z',
                        },
                    },
                    {
                        'MessageId': 'msg-12346',
                        'ReceiptHandle': 'hndl-12346',
                        'MD5OfBody': '6cd355',
                        'Body': 'Another message!',
                        'Attributes': {},
                    },
                ]
            })
        ),
        FakeOperation(
            'DeleteQueue',
            " <p>Deletes a queue.</p>\n ",
            params=[
                FakeParam('QueueName', required=True, ptype='string'),
            ],
            output=True,
            result=(None, True)
        ),
    ]


class CollectionDetailsTestCase(unittest.TestCase):
    def setUp(self):
        super(CollectionDetailsTestCase, self).setUp()
        self.test_dirs = [
            os.path.join(os.path.dirname(__file__), 'test_data')
        ]
        self.test_loader = ResourceJSONLoader(self.test_dirs)
        self.session = Session(FakeSession(TestCoreService()))

        self.cd = CollectionDetails(
            self.session,
            'test',
            'PipelineCollection',
            loader=self.test_loader
        )

    def test_init(self):
        self.assertEqual(self.cd.session, self.session)
        self.assertEqual(self.cd.service_name, 'test')
        self.assertEqual(self.cd.loader, self.test_loader)
        self.assertEqual(self.cd._loaded_data, None)
        self.assertEqual(self.cd._api_versions, None)

    def test_service_data_uncached(self):
        self.assertEqual(self.cd._loaded_data, None)

        data = self.cd.service_data
        self.assertEqual(len(data.keys()), 4)
        self.assertTrue('api_versions' in self.cd._loaded_data)

    def test_collection_data_uncached(self):
        self.assertEqual(self.cd._loaded_data, None)

        data = self.cd.collection_data
        self.assertEqual(len(data.keys()), 2)
        self.assertFalse('identifiers' in data)
        self.assertTrue('operations' in data)
        self.assertTrue('api_versions' in self.cd._loaded_data)

    def test_api_version_uncached(self):
        self.assertEqual(self.cd._api_versions, None)

        av = self.cd.api_versions
        self.assertEqual(av, [
            '2012-09-25',
        ])
        self.assertEqual(self.cd._api_versions, [
            '2012-09-25',
        ])

    def test_resource_uncached(self):
        self.assertEqual(self.cd._loaded_data, None)

        res = self.cd.resource
        self.assertEqual(res, 'Pipeline')
        self.assertTrue('api_versions' in self.cd._loaded_data)

    def test_cached(self):
        # Fake in data.
        self.cd._loaded_data = {
            'api_versions': [
                '20XX-MM-II',
            ],
            'hello': 'world',
        }

        data = self.cd.service_data
        av = self.cd.api_versions
        self.assertTrue('hello' in data)
        self.assertTrue('20XX-MM-II' in av)


class FakeConn(object):
    def __init__(self, *args, **kwargs):
        super(FakeConn, self).__init__()

    def create_pipeline(self, *args, **kwargs):
        return {
            'RequestId': '1234-1234-1234-1234',
            'Id': '1872baf45',
            'Title': 'A pipe',
        }


class PipeCollection(Collection):
    def update_params(self, conn_method_name, params):
        params['global'] = True
        return super(PipeCollection, self).update_params(conn_method_name, params)

    def update_params_create(self, params):
        params['created'] = True
        return params

    def post_process(self, conn_method_name, result):
        self.identifier = result.pop('Id')
        return result

    def post_process_create(self, result):
        self.created = True
        return result


class CollectionTestCase(unittest.TestCase):
    def setUp(self):
        super(CollectionTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.fake_details = CollectionDetails(
            self.session,
            'test',
            'PipeCollection'
        )
        self.fake_details._loaded_data = {
            'api_versions': ['something'],
            'collections': {
                'PipeCollection': {
                    'resource': 'Pipe',
                    'identifiers': [
                        {
                            'var_name': 'id',
                            'api_name': 'Id',
                        },
                    ],
                    'operations': {
                        'create': {
                            'api_name': 'CreatePipe',
                            'docs': '',
                            'params': {},
                        }
                    }
                }
            }
        }
        self.fake_conn = FakeConn()
        self.collection = PipeCollection(
            connection=self.fake_conn,
            id='1872baf45'
        )
        self.collection._details = self.fake_details

    def test_full_update_params(self):
        params = {
            'notify': True,
        }
        prepped = self.collection.full_update_params('create', params)
        self.assertEqual(prepped, {
            'global': True,
            'created': True,
            'notify': True,
        })

    def test_full_post_process(self):
        results = {
            'Id': '1872baf45',
            'Title': 'A pipe',
        }
        processed = self.collection.full_post_process('create', results)
        self.assertEqual(processed, {
            'Title': 'A pipe'
        })
        self.assertEqual(self.collection.created, True)

    def build_resource(self):
        class Pipe(object):
            def __init__(self, **kwargs):
                # Yuck yuck yuck. Fake fake fake.
                self.__dict__.update(kwargs)

        # Reach in to fake some data.
        # We'll test proper behavior with the integration tests.
        self.session.cache.set_resource('test', 'Pipe', Pipe)

        res_class = self.collection.build_resource({
            'test': 'data'
        })
        self.assertTrue(isinstance(res_class, Pipe))
        self.assertEqual(res_class.test, 'data')


class CollectionFactoryTestCase(unittest.TestCase):
    def setUp(self):
        super(CollectionFactoryTestCase, self).setUp()
        self.session = Session(FakeSession(TestCoreService()))
        self.test_dirs = [
            os.path.join(os.path.dirname(__file__), 'test_data')
        ]
        self.test_loader = ResourceJSONLoader(self.test_dirs)
        self.cd = CollectionDetails(
            self.session,
            'test',
            'PipelineCollection',
            loader=self.test_loader
        )
        self.cf = CollectionFactory(session=self.session, loader=self.test_loader)

    def test_init(self):
        self.assertEqual(self.cf.session, self.session)
        self.assertTrue(isinstance(self.cf.loader, ResourceJSONLoader))
        self.assertEqual(self.cf.base_collection_class, Collection)
        self.assertEqual(self.cf.details_class, CollectionDetails)

        # Test overrides (invalid for actual usage).
        import boto3
        cf = CollectionFactory(
            loader=False,
            base_collection_class=PipeCollection,
            details_class=True
        )
        self.assertEqual(cf.session, boto3.session)
        self.assertEqual(cf.loader, False)
        self.assertEqual(cf.base_collection_class, PipeCollection)
        self.assertEqual(cf.details_class, True)

    def test_build_class_name(self):
        self.assertEqual(
            self.cf._build_class_name('PipelineCollection'),
            'PipelineCollection'
        )
        self.assertEqual(
            self.cf._build_class_name('TestName'),
            'TestName'
        )

    def test_build_methods(self):
        attrs = self.cf._build_methods(self.cd)
        self.assertEqual(len(attrs), 4)
        self.assertTrue('create' in attrs)
        self.assertTrue('all' in attrs)
        self.assertTrue('test_role' in attrs)
        self.assertTrue('get' in attrs)

    def test_create_operation_method(self):
        class StubbyCollection(Collection):
            pass

        op_method = self.cf._create_operation_method('create', {
            "api_name": "CreatePipeline",
            "docs": "MAK U NU PIPLIN.",
            "params": {
                "id": {
                    "api_name": "Id",
                    "type": "string"
                }
            }
        })
        self.assertEqual(op_method.__name__, 'create')
        self.assertEqual(
            op_method.__doc__,
            'MAK U NU PIPLIN.'
        )

        # Assign it & call it.
        StubbyCollection._details = self.cd
        StubbyCollection.delete = op_method
        sr = StubbyCollection(connection=FakeConn())
        self.assertEqual(sr.delete(), {
            'Id': '1872baf45',
            'RequestId': '1234-1234-1234-1234',
            'Title': 'A pipe'
        })

    def test_construct_for(self):
        col_class = self.cf.construct_for('test', 'PipelineCollection')
