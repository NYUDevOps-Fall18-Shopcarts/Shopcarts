
     def test_delete_a_product(self):
        """ Delete a Product """
        product = new_product(user_id=1, product_id=1)
        product.save()
        self.assertEqual(len(new_product.all()), 1)
        # delete the pet and make sure it isn't in the database
        new_product.delete()
        self.assertEqual(len(new_product.all()), 0)

