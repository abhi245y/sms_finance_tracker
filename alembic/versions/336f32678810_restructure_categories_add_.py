"""restructure_categories_add_subcategories_and_seed_data

Revision ID: 336f32678810
Revises: e71bd987c3bf
Create Date: 2025-06-13 17:18:13.537791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Text


# revision identifiers, used by Alembic.
revision: str = '336f32678810'
down_revision: Union[str, None] = 'e71bd987c3bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define table schemas for bulk insert (helps with type safety and less verbose)
categories_table = table('categories',
    column('id', Integer),
    column('name', String),
    column('description', Text),
    column('display_order', Integer)
)

subcategories_table = table('subcategories',
    column('id', Integer),
    column('name', String),
    column('icon_name', String),
    column('display_order', Integer),
    column('parent_category_id', Integer)
)

# --- Seed Data ---
# IDs are manually assigned for predictable FK relationships during seeding.


CATEGORY_ID_OFFSET = 100 
SUBCATEGORY_ID_OFFSET = 1000

# Helper to generate IDs
def cat_id(offset): return CATEGORY_ID_OFFSET + offset
def subcat_id(offset): return SUBCATEGORY_ID_OFFSET + offset

# GENERAL Category (MUST be first for default subcategory)
GENERAL_CAT_ID = cat_id(0)
UNCATEGORIZED_SUBCAT_ID = subcat_id(0)

seed_categories_data = [
    {'id': GENERAL_CAT_ID, 'name': 'General', 'description': 'Default and miscellaneous items', 'display_order': 999},
    {'id': cat_id(1), 'name': 'Food & Drinks', 'description': 'Eating out, Swiggy, Zomato etc.', 'display_order': 0},
    {'id': cat_id(2), 'name': 'Groceries', 'description': 'Kitchen and other household supplies', 'display_order': 1},
    {'id': cat_id(3), 'name': 'Transport', 'description': 'Uber, Ola and other modes of transport', 'display_order': 2},
    {'id': cat_id(4), 'name': 'Shopping', 'description': 'Clothes, shoes, furniture etc.', 'display_order': 3},
    {'id': cat_id(5), 'name': 'Bill', 'description': 'Rent, Wi-fi, electricity and other bills', 'display_order': 4},
    {'id': cat_id(6), 'name': 'Subscription', 'description': 'Recurring payment to online services', 'display_order': 5},
    {'id': cat_id(7), 'name': 'EMI', 'description': 'Repayment of Loan', 'display_order': 6},
    {'id': cat_id(8), 'name': 'Credit Bill', 'description': 'Credit Card & BNPL services settlement', 'display_order': 7},
    {'id': cat_id(9), 'name': 'Investment', 'description': 'Money put towards investment', 'display_order': 8},
    {'id': cat_id(10), 'name': 'Support', 'description': 'Financial support for loved ones', 'display_order': 9},
    {'id': cat_id(11), 'name': 'Insurance', 'description': 'Payment towards insurance premiums', 'display_order': 10},
    {'id': cat_id(12), 'name': 'Tax', 'description': 'Income tax, property tax, e.t.c', 'display_order': 11},
    {'id': cat_id(13), 'name': 'Medical', 'description': 'Medicines, Doctor consulation etc.', 'display_order': 12},
    {'id': cat_id(14), 'name': 'Personal', 'description': 'Money spent on & for yourself', 'display_order': 13},
    {'id': cat_id(15), 'name': 'Fitness', 'description': 'Things to keep your biological machinery in tune', 'display_order': 14},
    {'id': cat_id(16), 'name': 'Services', 'description': 'Professional services provided for a fee', 'display_order': 15},
    {'id': cat_id(17), 'name': 'Entertainment', 'description': 'Movies, Concerts and other recreations', 'display_order': 16},
    {'id': cat_id(18), 'name': 'Events', 'description': 'Being social while putting a dent in your bank account', 'display_order': 17},
    {'id': cat_id(19), 'name': 'Travel', 'description': 'Exploration, fun and vacations!', 'display_order': 18},
    {'id': cat_id(20), 'name': 'Savings', 'description': 'For goals and dreams', 'display_order': 19},
    {'id': cat_id(21), 'name': 'Gift', 'description': 'Money gifted or spent buying gifts :)', 'display_order': 20},
    {'id': cat_id(22), 'name': 'Lent', 'description': 'Money lent with expectation of return', 'display_order': 21},
    {'id': cat_id(23), 'name': 'Donation', 'description': 'Contributions to charities and NGOs', 'display_order': 22},
    {'id': cat_id(24), 'name': 'Hidden Charges', 'description': "Banks's hidden subscription charges", 'display_order': 23},
    {'id': cat_id(25), 'name': 'Cash Withdrawal', 'description': 'Cash taken out from ATM or Bank', 'display_order': 24},
    {'id': cat_id(26), 'name': 'Return', 'description': 'Borrowed money is returned', 'display_order': 25},
    {'id': cat_id(27), 'name': 'Top-up', 'description': 'Money added to online wallets', 'display_order': 26},
    {'id': cat_id(28), 'name': 'Misc.', 'description': 'Everything else', 'display_order': 27},
]

seed_subcategories_data = [
    {'id': UNCATEGORIZED_SUBCAT_ID, 'name': 'Uncategorized', 'icon_name': 'fthr:tag', 'display_order': 0, 'parent_category_id': GENERAL_CAT_ID},

    # Food & Drinks (parent_id: cat_id(1))
    {'id': subcat_id(1), 'name': 'Eating out', 'icon_name': 'emoji:🍽️', 'display_order': 0, 'parent_category_id': cat_id(1)},
    {'id': subcat_id(2), 'name': 'Take Away', 'icon_name': 'emoji:🥡', 'display_order': 1, 'parent_category_id': cat_id(1)},
    {'id': subcat_id(3), 'name': 'Tea & Coffee', 'icon_name': 'emoji:☕', 'display_order': 2, 'parent_category_id': cat_id(1)},
    {'id': subcat_id(4), 'name': 'Fast Food', 'icon_name': 'emoji:🍔', 'display_order': 3, 'parent_category_id': cat_id(1)},
    {'id': subcat_id(5), 'name': 'Snacks', 'icon_name': 'emoji:🍿', 'display_order': 4, 'parent_category_id': cat_id(1)},

    # Groceries (parent_id: cat_id(2))
    {'id': subcat_id(6), 'name': 'Staples', 'icon_name': 'fthr:archive', 'display_order': 0, 'parent_category_id': cat_id(2)}, # Placeholder icon
    {'id': subcat_id(7), 'name': 'Vegetables', 'icon_name': 'emoji:🥦', 'display_order': 1, 'parent_category_id': cat_id(2)},
    {'id': subcat_id(8), 'name': 'Fruits', 'icon_name': 'emoji:🍌', 'display_order': 2, 'parent_category_id': cat_id(2)},
    {'id': subcat_id(9), 'name': 'Meat', 'icon_name': 'emoji:🥩', 'display_order': 3, 'parent_category_id': cat_id(2)},
    {'id': subcat_id(10), 'name': 'Eggs', 'icon_name': 'emoji:🥚', 'display_order': 4, 'parent_category_id': cat_id(2)},

    # Transport (parent_id: cat_id(3))
    {'id': subcat_id(11), 'name': 'Uber', 'icon_name': 'img:brand/uber.svg', 'display_order': 0, 'parent_category_id': cat_id(3)},
    {'id': subcat_id(12), 'name': 'Rapido', 'icon_name': 'emoji:🛵', 'display_order': 1, 'parent_category_id': cat_id(3)},
    {'id': subcat_id(13), 'name': 'Auto', 'icon_name': 'emoji:🛺', 'display_order': 2, 'parent_category_id': cat_id(3)},
    {'id': subcat_id(14), 'name': 'Cab', 'icon_name': 'emoji:🚕', 'display_order': 3, 'parent_category_id': cat_id(3)},
    {'id': subcat_id(15), 'name': 'Train', 'icon_name': 'emoji:🚆', 'display_order': 4, 'parent_category_id': cat_id(3)},
    
    # Shopping (parent_id: cat_id(4))
    {'id': subcat_id(16), 'name': 'Clothes', 'icon_name': 'fthr:shopping-bag', 'display_order': 0, 'parent_category_id': cat_id(4)}, # Placeholder, consider more specific
    {'id': subcat_id(17), 'name': 'Footwear', 'icon_name': 'fthr:award', 'display_order': 1, 'parent_category_id': cat_id(4)}, # Placeholder
    {'id': subcat_id(18), 'name': 'Electronics', 'icon_name': 'fthr:smartphone', 'display_order': 2, 'parent_category_id': cat_id(4)},
    {'id': subcat_id(19), 'name': 'Festival', 'icon_name': 'fthr:gift', 'display_order': 3, 'parent_category_id': cat_id(4)},
    {'id': subcat_id(20), 'name': 'Video games', 'icon_name': 'fthr:play-circle', 'display_order': 4, 'parent_category_id': cat_id(4)},


    # Bill (parent_id: cat_id(5))
    {'id': subcat_id(21), 'name': 'Phone', 'icon_name': 'fthr:phone', 'display_order': 0, 'parent_category_id': cat_id(5)},
    {'id': subcat_id(22), 'name': 'Rent', 'icon_name': 'fthr:home', 'display_order': 1, 'parent_category_id': cat_id(5)},
    {'id': subcat_id(23), 'name': 'Water', 'icon_name': 'fthr:droplet', 'display_order': 2, 'parent_category_id': cat_id(5)},
    {'id': subcat_id(24), 'name': 'Electricity', 'icon_name': 'fthr:zap', 'display_order': 3, 'parent_category_id': cat_id(5)},
    {'id': subcat_id(25), 'name': 'Gas', 'icon_name': 'fthr:thermometer', 'display_order': 4, 'parent_category_id': cat_id(5)}, # Placeholder

    # Subscription (parent_id: cat_id(6))
    {'id': subcat_id(26), 'name': 'Software', 'icon_name': 'fthr:disc', 'display_order': 0, 'parent_category_id': cat_id(6)},
    {'id': subcat_id(27), 'name': 'News', 'icon_name': 'fthr:file-text', 'display_order': 1, 'parent_category_id': cat_id(6)},
    {'id': subcat_id(28), 'name': 'Netflix', 'icon_name': 'img:brand/netflix.svg', 'display_order': 2, 'parent_category_id': cat_id(6)},
    {'id': subcat_id(29), 'name': 'Prime', 'icon_name': 'img:brand/amazonprime.svg', 'display_order': 3, 'parent_category_id': cat_id(6)},
    {'id': subcat_id(30), 'name': 'YouTube', 'icon_name': 'img:brand/youtube.svg', 'display_order': 4, 'parent_category_id': cat_id(6)},

    # EMI (parent_id: cat_id(7))
    {'id': subcat_id(31), 'name': 'Electronics', 'icon_name': 'fthr:smartphone', 'display_order': 0, 'parent_category_id': cat_id(7)},
    {'id': subcat_id(32), 'name': 'House', 'icon_name': 'fthr:home', 'display_order': 1, 'parent_category_id': cat_id(7)},
    {'id': subcat_id(33), 'name': 'Vehicle', 'icon_name': 'fthr:truck', 'display_order': 2, 'parent_category_id': cat_id(7)},
    {'id': subcat_id(34), 'name': 'Education', 'icon_name': 'fthr:book-open', 'display_order': 3, 'parent_category_id': cat_id(7)},
    {'id': subcat_id(35), 'name': 'Others', 'icon_name': 'fthr:tag', 'display_order': 4, 'parent_category_id': cat_id(7)},

    # Credit Bill (parent_id: cat_id(8))
    {'id': subcat_id(36), 'name': 'Credit card', 'icon_name': 'fthr:credit-card', 'display_order': 0, 'parent_category_id': cat_id(8)},
    {'id': subcat_id(37), 'name': 'Simpl', 'icon_name': 'img:brand/simpl.svg', 'display_order': 1, 'parent_category_id': cat_id(8)},
    {'id': subcat_id(38), 'name': 'Slice', 'icon_name': 'img:brand/slice.svg', 'display_order': 2, 'parent_category_id': cat_id(8)},
    {'id': subcat_id(39), 'name': 'Lazypay', 'icon_name': 'img:brand/lazypay.svg', 'display_order': 3, 'parent_category_id': cat_id(8)},
    {'id': subcat_id(40), 'name': 'Amazon Pay', 'icon_name': 'img:brand/amazonpay.svg', 'display_order': 4, 'parent_category_id': cat_id(8)},

    # Investment (parent_id: cat_id(9))
    {'id': subcat_id(41), 'name': 'Mutual Funds', 'icon_name': 'fthr:bar-chart-2', 'display_order': 0, 'parent_category_id': cat_id(9)},
    {'id': subcat_id(42), 'name': 'Stocks', 'icon_name': 'fthr:trending-up', 'display_order': 1, 'parent_category_id': cat_id(9)},
    {'id': subcat_id(43), 'name': 'IPO', 'icon_name': 'fthr:briefcase', 'display_order': 2, 'parent_category_id': cat_id(9)},
    {'id': subcat_id(44), 'name': 'PPF', 'icon_name': 'fthr:shield', 'display_order': 3, 'parent_category_id': cat_id(9)},
    {'id': subcat_id(45), 'name': 'NPS', 'icon_name': 'fthr:shield', 'display_order': 4, 'parent_category_id': cat_id(9)},
    
    # Support (parent_id: cat_id(10))
    {'id': subcat_id(46), 'name': 'Parents', 'icon_name': 'fthr:users', 'display_order': 0, 'parent_category_id': cat_id(10)},
    {'id': subcat_id(47), 'name': 'Spouse', 'icon_name': 'fthr:heart', 'display_order': 1, 'parent_category_id': cat_id(10)},
    {'id': subcat_id(48), 'name': 'Mom', 'icon_name': 'emoji:👩', 'display_order': 2, 'parent_category_id': cat_id(10)},
    {'id': subcat_id(49), 'name': 'Dad', 'icon_name': 'emoji:👨', 'display_order': 3, 'parent_category_id': cat_id(10)},
    {'id': subcat_id(50), 'name': 'Pocket Money', 'icon_name': 'fthr:dollar-sign', 'display_order': 4, 'parent_category_id': cat_id(10)},

    # Insurance (parent_id: cat_id(11))
    {'id': subcat_id(51), 'name': 'Health', 'icon_name': 'fthr:plus-circle', 'display_order': 0, 'parent_category_id': cat_id(11)},
    {'id': subcat_id(52), 'name': 'Vehicle', 'icon_name': 'fthr:truck', 'display_order': 1, 'parent_category_id': cat_id(11)},
    {'id': subcat_id(53), 'name': 'Life', 'icon_name': 'fthr:activity', 'display_order': 2, 'parent_category_id': cat_id(11)},
    {'id': subcat_id(54), 'name': 'Electronics', 'icon_name': 'fthr:smartphone', 'display_order': 3, 'parent_category_id': cat_id(11)}, # Assuming insurance for electronics
    {'id': subcat_id(55), 'name': 'Others', 'icon_name': 'fthr:tag', 'display_order': 4, 'parent_category_id': cat_id(11)},

    # Tax (parent_id: cat_id(12))
    {'id': subcat_id(56), 'name': 'Income Tax', 'icon_name': 'fthr:file-text', 'display_order': 0, 'parent_category_id': cat_id(12)},
    {'id': subcat_id(57), 'name': 'GST', 'icon_name': 'fthr:file-text', 'display_order': 1, 'parent_category_id': cat_id(12)},
    {'id': subcat_id(58), 'name': 'Property Tax', 'icon_name': 'fthr:home', 'display_order': 2, 'parent_category_id': cat_id(12)},
    {'id': subcat_id(59), 'name': 'Others', 'icon_name': 'fthr:tag', 'display_order': 3, 'parent_category_id': cat_id(12)},

    # Medical (parent_id: cat_id(13))
    {'id': subcat_id(60), 'name': 'Medicines', 'icon_name': 'fthr:thermometer', 'display_order': 0, 'parent_category_id': cat_id(13)}, # Placeholder
    {'id': subcat_id(61), 'name': 'Hospital', 'icon_name': 'fthr:plus-square', 'display_order': 1, 'parent_category_id': cat_id(13)},
    {'id': subcat_id(62), 'name': 'Clinic', 'icon_name': 'fthr:activity', 'display_order': 2, 'parent_category_id': cat_id(13)},
    {'id': subcat_id(63), 'name': 'Dentist', 'icon_name': 'emoji:🦷', 'display_order': 3, 'parent_category_id': cat_id(13)},
    {'id': subcat_id(64), 'name': 'Lab test', 'icon_name': 'fthr:thermometer', 'display_order': 4, 'parent_category_id': cat_id(13)}, # Placeholder

    # Personal (parent_id: cat_id(14))
    {'id': subcat_id(65), 'name': 'Self-care', 'icon_name': 'fthr:smile', 'display_order': 0, 'parent_category_id': cat_id(14)},
    {'id': subcat_id(66), 'name': 'Grooming', 'icon_name': 'emoji:✂️', 'display_order': 1, 'parent_category_id': cat_id(14)},
    {'id': subcat_id(67), 'name': 'Hobbies', 'icon_name': 'fthr:feather', 'display_order': 2, 'parent_category_id': cat_id(14)},
    {'id': subcat_id(68), 'name': 'Vices', 'icon_name': 'emoji:🚬', 'display_order': 3, 'parent_category_id': cat_id(14)}, # Example, use generic if preferred
    {'id': subcat_id(69), 'name': 'Therapy', 'icon_name': 'fthr:message-circle', 'display_order': 4, 'parent_category_id': cat_id(14)},

    # Fitness (parent_id: cat_id(15))
    {'id': subcat_id(70), 'name': 'Gym', 'icon_name': 'fthr:activity', 'display_order': 0, 'parent_category_id': cat_id(15)},
    {'id': subcat_id(71), 'name': 'Badminton', 'icon_name': 'emoji:🏸', 'display_order': 1, 'parent_category_id': cat_id(15)},
    {'id': subcat_id(72), 'name': 'Football', 'icon_name': 'emoji:⚽', 'display_order': 2, 'parent_category_id': cat_id(15)},
    {'id': subcat_id(73), 'name': 'Cricket', 'icon_name': 'emoji:🏏', 'display_order': 3, 'parent_category_id': cat_id(15)},
    {'id': subcat_id(74), 'name': 'Classes', 'icon_name': 'fthr:calendar', 'display_order': 4, 'parent_category_id': cat_id(15)},

    # Services (parent_id: cat_id(16))
    {'id': subcat_id(75), 'name': 'Laundry', 'icon_name': 'fthr:refresh-cw', 'display_order': 0, 'parent_category_id': cat_id(16)}, # Placeholder
    {'id': subcat_id(76), 'name': 'Tailor', 'icon_name': 'emoji:🧵', 'display_order': 1, 'parent_category_id': cat_id(16)},
    {'id': subcat_id(77), 'name': 'Courier', 'icon_name': 'fthr:send', 'display_order': 2, 'parent_category_id': cat_id(16)},
    {'id': subcat_id(78), 'name': 'Carpenter', 'icon_name': 'fthr:tool', 'display_order': 3, 'parent_category_id': cat_id(16)},
    {'id': subcat_id(79), 'name': 'Plumber', 'icon_name': 'fthr:tool', 'display_order': 4, 'parent_category_id': cat_id(16)},

    # Entertainment (parent_id: cat_id(17))
    {'id': subcat_id(80), 'name': 'Movies', 'icon_name': 'fthr:film', 'display_order': 0, 'parent_category_id': cat_id(17)},
    {'id': subcat_id(81), 'name': 'Shows', 'icon_name': 'fthr:tv', 'display_order': 1, 'parent_category_id': cat_id(17)},
    {'id': subcat_id(82), 'name': 'Bowling', 'icon_name': 'emoji:🎳', 'display_order': 2, 'parent_category_id': cat_id(17)},
    {'id': subcat_id(83), 'name': 'Others', 'icon_name': 'fthr:tag', 'display_order': 3, 'parent_category_id': cat_id(17)},
    # Duplicate 'Others' in screenshot, ensure unique names or handle appropriately. Assuming one 'Others' per group.
    
    # Events (parent_id: cat_id(18))
    {'id': subcat_id(84), 'name': 'Party', 'icon_name': 'emoji:🎉', 'display_order': 0, 'parent_category_id': cat_id(18)},
    {'id': subcat_id(85), 'name': 'Spiritual', 'icon_name': 'emoji:🕉️', 'display_order': 1, 'parent_category_id': cat_id(18)}, # Or fthr:moon
    {'id': subcat_id(86), 'name': 'Wedding', 'icon_name': 'fthr:heart', 'display_order': 2, 'parent_category_id': cat_id(18)},
    {'id': subcat_id(87), 'name': 'Others', 'icon_name': 'fthr:tag', 'display_order': 3, 'parent_category_id': cat_id(18)},
    
    # Travel (parent_id: cat_id(19))
    {'id': subcat_id(88), 'name': 'Activities', 'icon_name': 'fthr:compass', 'display_order': 0, 'parent_category_id': cat_id(19)},
    {'id': subcat_id(89), 'name': 'Camping', 'icon_name': 'emoji:🏕️', 'display_order': 1, 'parent_category_id': cat_id(19)},
    {'id': subcat_id(90), 'name': 'Hotel', 'icon_name': 'fthr:briefcase', 'display_order': 2, 'parent_category_id': cat_id(19)}, # Placeholder
    {'id': subcat_id(91), 'name': 'Hostel', 'icon_name': 'fthr:home', 'display_order': 3, 'parent_category_id': cat_id(19)},
    {'id': subcat_id(92), 'name': 'Airbnb', 'icon_name': 'img:brand/airbnb.svg', 'display_order': 4, 'parent_category_id': cat_id(19)},

    # Savings (parent_id: cat_id(20))
    {'id': subcat_id(93), 'name': 'Savings', 'icon_name': 'fthr:database', 'display_order': 0, 'parent_category_id': cat_id(20)}, # Placeholder

    # Gift (parent_id: cat_id(21))
    {'id': subcat_id(94), 'name': 'Gift', 'icon_name': 'fthr:gift', 'display_order': 0, 'parent_category_id': cat_id(21)},

    # Lent (parent_id: cat_id(22))
    {'id': subcat_id(95), 'name': 'Lent', 'icon_name': 'fthr:arrow-up-right', 'display_order': 0, 'parent_category_id': cat_id(22)},

    # Donation (parent_id: cat_id(23))
    {'id': subcat_id(96), 'name': 'Donation', 'icon_name': 'fthr:heart', 'display_order': 0, 'parent_category_id': cat_id(23)},

    # Hidden Charges (parent_id: cat_id(24))
    {'id': subcat_id(97), 'name': 'Hidden Charges', 'icon_name': 'fthr:eye-off', 'display_order': 0, 'parent_category_id': cat_id(24)},

    # Cash Withdrawal (parent_id: cat_id(25))
    {'id': subcat_id(98), 'name': 'Cash Withdrawal', 'icon_name': 'fthr:dollar-sign', 'display_order': 0, 'parent_category_id': cat_id(25)},

    # Return (parent_id: cat_id(26))
    {'id': subcat_id(99), 'name': 'Return', 'icon_name': 'fthr:arrow-left', 'display_order': 0, 'parent_category_id': cat_id(26)},

    # Top-up (parent_id: cat_id(27))
    {'id': subcat_id(100), 'name': 'UPI Lite', 'icon_name': 'img:brand/upilite.svg', 'display_order': 0, 'parent_category_id': cat_id(27)},
    {'id': subcat_id(101), 'name': 'Paytm', 'icon_name': 'img:brand/paytm.svg', 'display_order': 1, 'parent_category_id': cat_id(27)},
    {'id': subcat_id(102), 'name': 'Amazon', 'icon_name': 'img:brand/amazon.svg', 'display_order': 2, 'parent_category_id': cat_id(27)},
    {'id': subcat_id(103), 'name': 'PhonePe', 'icon_name': 'img:brand/phonepe.svg', 'display_order': 3, 'parent_category_id': cat_id(27)},
    {'id': subcat_id(104), 'name': 'Others', 'icon_name': 'fthr:tag', 'display_order': 4, 'parent_category_id': cat_id(27)},
    
    # Misc. (parent_id: cat_id(28))
    {'id': subcat_id(105), 'name': 'Tip', 'icon_name': 'fthr:thumbs-up', 'display_order': 0, 'parent_category_id': cat_id(28)},
    {'id': subcat_id(106), 'name': 'Verification', 'icon_name': 'fthr:check-circle', 'display_order': 1, 'parent_category_id': cat_id(28)},
    {'id': subcat_id(107), 'name': 'Forex', 'icon_name': 'fthr:globe', 'display_order': 2, 'parent_category_id': cat_id(28)},
    {'id': subcat_id(108), 'name': 'Deposit', 'icon_name': 'fthr:download', 'display_order': 3, 'parent_category_id': cat_id(28)},
    {'id': subcat_id(109), 'name': 'Gift Card', 'icon_name': 'fthr:gift', 'display_order': 4, 'parent_category_id': cat_id(28)},
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Step 1: Create 'subcategories' table
    op.create_table('subcategories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('icon_name', sa.String(length=100), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('parent_category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['parent_category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'parent_category_id', name='uq_subcategory_name_parent')
    )
    op.create_index(op.f('ix_subcategories_id'), 'subcategories', ['id'], unique=False)
    op.create_index(op.f('ix_subcategories_parent_category_id'), 'subcategories', ['parent_category_id'], unique=False)

    # Step 2: Modify 'categories' table
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))
  

    # Step 3 & 4: Seed categories and subcategories
    # Ensure GENERAL_CAT_ID and UNCATEGORIZED_SUBCAT_ID are correctly defined from the seed data
    op.bulk_insert(categories_table, seed_categories_data)
    op.bulk_insert(subcategories_table, seed_subcategories_data)


    # Step 5: Modify 'transactions' table - Part 1: Add subcategory_id as nullable
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('subcategory_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_transactions_subcategory_id'), ['subcategory_id'], unique=False)


    # Step 5.1: Populate new subcategory_id using a direct SQL execution
    # This runs OUTSIDE the batch_alter_table context for the UPDATE to see the newly added column.
    # UNCATEGORIZED_SUBCAT_ID must be defined from your seed data constants.
    op.execute(f"UPDATE transactions SET subcategory_id = {UNCATEGORIZED_SUBCAT_ID}")


    # Step 5.2: Modify 'transactions' table - Part 2: Make subcategory_id non-nullable and add FK
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.alter_column('subcategory_id',
                              existing_type=sa.INTEGER(),
                              nullable=False)
        
        batch_op.create_foreign_key(
            "fk_transactions_subcategory_id_subcategories", 
            'subcategories',                                
            ['subcategory_id'],                             
            ['id']                                         
        )

        try:
             batch_op.drop_constraint('fk_transactions_category_id_categories', type_='foreignkey')
        except Exception as e:
            print(f"INFO: Skipping drop of old category FK constraint 'fk_transactions_category_id_categories', might not exist or name differs: {e}")

        try:
            batch_op.drop_index('ix_transactions_category_id') 
        except Exception as e:
             print(f"INFO: Skipping drop of old category_id index 'ix_transactions_category_id', might not exist: {e}")
        try:
            batch_op.drop_column('category_id')
        except Exception as e:
            print(f"INFO: Skipping drop of old category_id column, might not exist: {e}")
    # ### end Alembic commands ###
    
def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_constraint("fk_transactions_subcategory_id_subcategories", type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_transactions_subcategory_id'))
        batch_op.drop_column('subcategory_id')

        batch_op.add_column(sa.Column('category_id', sa.INTEGER(), nullable=True))
        batch_op.create_index('ix_transactions_category_id', ['category_id'], unique=False)


    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('display_order')
        batch_op.drop_column('description')

    op.drop_index(op.f('ix_subcategories_parent_category_id'), table_name='subcategories')
    op.drop_index(op.f('ix_subcategories_id'), table_name='subcategories')
    op.drop_table('subcategories')
    
    # ### end Alembic commands ###