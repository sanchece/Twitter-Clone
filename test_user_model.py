"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        # u1 = User.signup("test1", "email1@email.com", "password", None)
        # uid1 = 1111
        # u1.id = uid1

        # u2 = User.signup("test2", "email2@email.com", "password", None)
        # uid2 = 2222
        # u2.id = uid2

        # db.session.commit()

        # u1 = User.query.get(uid1)
        # u2 = User.query.get(uid2)

        # self.u1 = u1
        # self.uid1 = uid1

        # self.u2 = u2
        # self.uid2 = uid2

        # self.client = app.test_client()
     
    
        grizzly=User.signup(
            "grizzly",
            "grizzly@hotmail.com",
            "secret",
            "https://cowboystatedaily.com/wp-content/uploads/2020/05/grizzly-bear-spray-2048x1152.jpg"
        )
 
        yogi=User.signup(
            "yogi",
            "yogi@hotmail.com",
            "secret2",
            "https://www.toledoblade.com/image/2010/12/17/1140x_a10-7_cTC/Yogi-Bear-is-a-light-disappointing-pic-a-nic.jpg"
        )
        grizzly_id=300
        grizzly.id=grizzly_id
        yogi_id=400
        yogi.id=yogi_id
        db.session.commit()        
        grizzly=User.query.get(grizzly_id)
        self.grizzly=grizzly
        self.yogi=User.query.get(yogi_id)
        self.client = app.test_client()
    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_follows(self):
        self.yogi.following.append(self.grizzly)
        db.session.commit()
        self.assertEqual(len(self.grizzly.following), 0)
        self.assertEqual(len(self.grizzly.followers), 1)
        self.assertEqual(len(self.yogi.following), 1)
        self.assertEqual(len(self.yogi.followers), 0)
        self.assertEqual(self.grizzly.followers[0].id, self.yogi.id)
        self.assertEqual(self.yogi.following[0].id, self.grizzly.id)        
        self.assertTrue(self.yogi.is_following(self.grizzly))
        self.assertFalse(self.grizzly.is_following(self.yogi))
        self.assertTrue(self.grizzly.is_followed_by(self.yogi))
        self.assertFalse(self.yogi.is_followed_by(self.grizzly))
    
    def test_user_signup(self):
        smokey = User.signup("Smokey", "smokey@gmail.com", "fudgefire", "https://www.twincities.com/wp-content/uploads/2019/08/smokey-1.jpg")
        smokey.id=500
        db.session.commit()

        smokey_account=User.query.get(500)
        self.assertEqual(smokey_account.username, "Smokey")
        self.assertNotEqual(smokey_account.password, "fudgefire")

    def test_user_signup_invalids(self):
        baloo= User.signup(None,"smokey","jungle",None)
        baloo.id=600
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()