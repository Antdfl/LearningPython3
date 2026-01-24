# def build_profile(first, last, **user_info):
#     """Build a dictionary containing everything we know about a user.""" 
#     user_info['first_name'] = first
#     user_info['last_name'] = last
#     return user_info

# user_profile = build_profile('albert', 'einstein',
#                              location='princeton',
#                              field='physics')
# print(user_profile)

def car(manufacturer, model, **car_info):
    """Build a dictionary containing everything we know about a car."""
    car_info['manufacturer'] = manufacturer
    car_info['model'] = model
    car_info = dict(reversed(list(car_info.items())))
    return car_info

car_profile = car('subaru', 'outback',
                  color='blue',
                  tow_package=True,
                  accessory_version='Titanium',
                  seats='5'
                  )
print(car_profile)