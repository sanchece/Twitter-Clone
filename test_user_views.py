import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows
from app import app, CURR_USER_KEY

os.environ['DATABASE_URL'] = "postgresql:///warbler"
app.config['WTF_CSRF_ENABLED'] = False
# db.drop_all()
# db.create_all()

class MessageViewTestCase(TestCase):

    def setUp(self):

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


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")
            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@grizzly", str(resp.data))
            self.assertIn("@yogi", str(resp.data))


    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))

    def setup_messages(self):
        mYogi=Message(id=450,text="im yogi",user_id=400)
        mGrizzly=Message(id=350,text="i'm grizzly",user_id=self.grizzly_id)
        mUser=Message(id=150,text="i'm a test user",user_id=self.testuser_id)
        db.session.add_all([mGrizzly,mYogi,mUser])
        db.session.commit()
        l1 = Likes(user_id=self.yogi_id, message_id=350)
        db.session.add(l1)
        db.session.commit()

    def test_add_like(self):
        self.setup_messages()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/users/add_like/150", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==150).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_like(self):
        self.setup_messages()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.yogi_id

            resp = c.post("/users/add_like/350", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            likes = Likes.query.filter(Likes.message_id==350).all()
            self.assertEqual(len(likes), 0)
            # self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_unauthenticated_like(self):
        self.setup_messages()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 55555

            resp = c.post("/users/add_like/150", follow_redirects=True)
            self.assertNotEqual(resp.status_code, 200)

