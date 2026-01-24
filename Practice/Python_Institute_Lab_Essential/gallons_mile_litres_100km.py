def liters_100km_to_miles_gallon(liters):
 miles_gallons =(100 * 3.785411784)/(1.609344*liters)
 return miles_gallons

def miles_gallon_to_liters_100km(miles):
  liters100km = (100 * 3.785411784)/(1.609344*miles)
  return liters100km

print(liters_100km_to_miles_gallon(3.9))
print(liters_100km_to_miles_gallon(7.5))
print(liters_100km_to_miles_gallon(10.))
print(miles_gallon_to_liters_100km(60.3))
print(miles_gallon_to_liters_100km(31.4))
print(miles_gallon_to_liters_100km(23.5))
