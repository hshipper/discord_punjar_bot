'''
functions for collating data to write to firestore
mostly needed for initial setup
'''
from datetime import date

# make a document for each member in the channel if they don't have one yet


def create_user_documents(self, bot, db):
    user_ids = [user.id for user in bot.users]
    query = db.collection(u'puns').where(u'id', u'not-in', str(user_ids))
    results = query.stream()
    batch = db.batch()
    for result in results:
        ref = db.collection(u'puns').document(result.id).set({
            u'date_added': date.today()
        })
        batch.set(ref)
    batch.commit()
