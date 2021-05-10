import os
from unittest import TestCase
from models import db, connect_db, Message, User, Likes, Follows
from app import app, CURR_USER_KEY

os.environ['DATABASE_URL'] = "postgresql:///warbler"
app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.grizzly=User.signup(
            username="grizzly",
            email="grizzly@hotmail.com",
            password="secret",
            image_url="https://cowboystatedaily.com/wp-content/uploads/2020/05/grizzly-bear-spray-2048x1152.jpg"
        )
        self.grizzly_id=300
        self.grizzly.id=self.grizzly_id
        db.session.commit()

        self.grizzly = User.query.get(self.grizzly_id)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        mGrizzly=Message(id=350,text="im grizzly",user_id=self.grizzly_id)
        db.session.add(mGrizzly)
        db.session.commit()

        self.assertEqual(len(self.grizzly.messages), 1)
        self.assertEqual(self.grizzly.messages[0].text, "im grizzly")

    def test_message_likes(self):
        yogi=User.signup(
            username="yogi",
            email="yogi@hotmail.com",
            password="secret2",
            image_url="https://www.toledoblade.com/image/2010/12/17/1140x_a10-7_cTC/Yogi-Bear-is-a-light-disappointing-pic-a-nic.jpg"
        )

        yogi_id=400
        yogi.id=yogi_id
        db.session.commit()
        mGrizzly=Message(id=350,text="im grizzly",user_id=self.grizzly_id)
        mYogi=Message(id=450,text="im yogi",user_id=400)


        db.session.add_all([mYogi,mGrizzly])
        db.session.commit()
        yogi.likes.append(mGrizzly)
        db.session.commit()
        like = Likes.query.filter(Likes.user_id == yogi_id).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, mGrizzly.id)


        