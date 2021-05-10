"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User,Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.grizzly=User.signup(
            username="grizzly",
            email="grizzly@hotmail.com",
            password="secret",
            image_url="https://cowboystatedaily.com/wp-content/uploads/2020/05/grizzly-bear-spray-2048x1152.jpg"
        )
        self.grizzly_id=300
        self.grizzly.id=self.grizzly_id

        self.yogi=User.signup(
            username="yogi",
            email="yogi@hotmail.com",
            password="secret2",
            image_url="https://www.toledoblade.com/image/2010/12/17/1140x_a10-7_cTC/Yogi-Bear-is-a-light-disappointing-pic-a-nic.jpg"
        )
        self.yogi_id=400
        self.yogi.id=self.yogi_id
        db.session.commit()

        # mYogi=Message(id=450,text="im yogi",user_id=400)
        # mGrizzly=Message(id=350,text="i'm grizzly",user_id=self.grizzly_id)
        # mUser=Message(id=150,text="i'm a test user",user_id=self.testuser_id)
        # db.session.add_all([mGrizzly,mYogi,mUser])
        # db.session.commit()


        # like1=Likes(user_id=self.yogi_id,message_id=350)
        # db.session.add(like1)
        # db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    def test_invalid_user_add_message(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = 10203040
            res=client.post("/messages/new",data={"text":"hello"}, follow_redirects=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("Access unauthorized",str(res.data))

    def test_display_message(self):
        mYogi=Message(id=450,text="i am yogi",user_id=self.yogi_id)
        db.session.add(mYogi)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            mYogi = Message.query.get(450)
            resp = c.get(f'/messages/{mYogi.id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(mYogi.text, str(resp.data))

    def test_display_message_invalid(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            resp = c.get('/messages/100008')
            self.assertNotEqual(resp.status_code, 200)

    def test_message_delete(self):
        mtest = Message(
            id=1234,
            text="successfull delete",
            user_id=self.testuser_id
        )
        db.session.add(mtest)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            mtest = Message.query.get(1234)
            self.assertIsNone(mtest)

    def test_message_delete_unauthorized(self): 
        mtest = Message(
            id=2000,
            text="successfull delete",
            user_id=self.testuser_id
        )
        db.session.add(mtest)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.yogi_id

            resp = c.post("/messages/2000/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            m = Message.query.get(2000)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):

        mtest = Message(
            id=2000,
            text="successfull delete",
            user_id=self.testuser_id
        )
        db.session.add(mtest)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/2000/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            m = Message.query.get(2000)
            self.assertIsNotNone(mtest)
       

    # def test_users(self):
    #     with self.client as browser:
    #         resp=browser.get("/users")
    #         self.assertIn("testuser",str(resp.data))

    # # def test_user_like_message(self):
    #     mfromGrizzly=Message.query.filter(Message.user_id==300).one()
    #     likefromYogi=Likes.query.filter(Likes.user_id==self.yogi_id)
    #     self.assertIsNotNone(likefromYogi)

    #     with self.client as browser:
    #         with browser.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.yogi_id

    #         resp = browser.post(f"/users/add_like/{mfromGrizzly.id}", follow_redirects=True)
    #         self.assertEqual(resp.status_code, 200)

