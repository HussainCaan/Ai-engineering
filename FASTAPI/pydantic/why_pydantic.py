
def insert_data(name:str, age: int): # if we use type hints here, it will not enforce the type validation. It is just for documentation purposes. It does not produce error if we pass a string instead of an integer for age.
    if type(name) != str or type(age) != int: # This is a manual type validation. We are checking the type of name and age and if it is not of the expected type, we are raising a ValueError. But this method is not scalable and it is not efficient. We have to write this type of validation for every function and it can become very cumbersome.
        raise ValueError("Invalid data type for name or age")
    print(name, age)
    print("Data inserted successfully")


insert_data("khan", "twenty four") # This will work but age is expected to be an integer, not a string. so No type validation is happening here.

