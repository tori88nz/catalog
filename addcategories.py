from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Add Categories to the DB
category1 = Category(name="Face")

session.add(category1)
session.commit()

category2 = Category(name="Eyes")

session.add(category2)
session.commit()

category3 = Category(name="Lips")

session.add(category3)
session.commit()

category4 = Category(name="Nails")

session.add(category4)
session.commit()

category5 = Category(name="Make-up Remover")

session.add(category5)
session.commit()

category6 = Category(name="Skincare")

session.add(category6)
session.commit()

category7 = Category(name="Hair")

session.add(category7)
session.commit()

category8 = Category(name="Tools & Brushes")

session.add(category8)
session.commit()

category9 = Category(name="Bath & Body")

session.add(category9)
session.commit()

print "Woohoo! Successfully added categories to your database! Go you!!"
print "Attempting to add user..."

# Add user to database
user1 = User(name="Tori Williams", email="tori.williams@hotmail.co.nz")

session.add(user1)
session.commit()

print "Yay! User Added!"
print "Now lets add an item..."

# Add items to database
item1 = Item(name="Foundation Brush", description=("Flexible bristles and "
                                                   "gently tapered edges make "
                                                   "this brush perfect for "
                                                   "applying & blending "
                                                   "cream foundations with a "
                                                   "streak-free finish. "
                                                   "The dome shape allows the "
                                                   "bristles to blend as they "
                                                   "brush. The result is an "
                                                   "even, flawless finish."),
             category_id=1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Body Wash", description=("Refresh skin all over with "
                                            "sweet smelling suds made with "
                                            "natural exfoliants and extracts. "
                                            "Feel oh-so-fresh from head to "
                                            "toe..."),
             category_id=9, user_id=1)
session.add(item2)
session.commit()

item3 = Item(name="Eyeshadow", description=("Use eyeshadows to make your eyes "
                                            "pop, from essential palettes to "
                                            "glitter eyeshadow and matte "
                                            "eyeshadow."),
             category_id=2, user_id=1)
session.add(item3)
session.commit()

item4 = Item(name="Shampoo", description=("Cleansing hair care for dry "
                                          "damaged & thin hair. Natural "
                                          "nourishing hair care with "
                                          "volumizing, thickening & color- "
                                          "protecting shampoos for shiny "
                                          "healthy hair."),
             category_id=7, user_id=1)
session.add(item4)
session.commit()

item5 = Item(name="Lip Gloss", description=("Achieve glossy, high-shine lips "
             "with our range of sheer tints..."), category_id=3, user_id=1)
session.add(item5)
session.commit()

item6 = Item(name="Makeup Removing Cloth", description=("Before washing up "
                                                        "with your daily "
                                                        "cleanser, dislodge "
                                                        "the stubborn makeup "
                                                        "with a remover "
                                                        "designed to take off "
                                                        "all those can't stop "
                                                        "won't stop "
                                                        "cosmetics"),
             category_id=5, user_id=1)
session.add(item6)
session.commit()

item7 = Item(name="Nail Polish", description=("Long-lasting nail polish "
             "dries down to a high-shine finish."), category_id=4, user_id=1)
session.add(item7)
session.commit()

item8 = Item(name="Cleanser", description=("Remove make-up, dead skin cells, "
                                           "oil, dirt, and other types of "
                                           "pollutants from the skin of the "
                                           "face."),
             category_id=6, user_id=1)
session.add(item8)
session.commit()

item9 = Item(name="Blusher Brush", description=("Unsurpassed for sweeping on "
                                                "colour and defining cheeks."),
             category_id=8, user_id=1)
session.add(item9)
session.commit()


print "Awesome, your items have been added :)"
print "catalogwithusers.db Successfully updated!!"
print "Your Amaze!!"
