'''
functions for collating data to write to firestore
mostly needed for initial setup
'''
import datetime

# make a document for each member in the channel if they don't have one yet


def create_user_documents(self):
    user_ids = [user.id for user in self.bot.users if not user.bot]
    string_user_ids = [str(user_id) for user_id in user_ids]
    batch = self.db.batch()
    for user in string_user_ids:
        user_doc = self.db.collection(u'puns').document(user).get()
        if not user_doc.exists:
            print(f'{user} needs to be added to database')
            ref = self.db.collection(u'puns').document(user)
            batch.set(ref, {u'date_added': datetime.datetime.now(),
                            u'pun_count': 0,
                            u'last_pun': None})
    print('All new users have been added!')
    batch.commit()
