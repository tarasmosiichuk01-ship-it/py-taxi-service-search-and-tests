from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Manufacturer, Car

MANUFACTURER_URL = reverse("taxi:manufacturer-list")


class PublicManufacturerTests(TestCase):
    def test_login_required(self):
        res = self.client.get(MANUFACTURER_URL)
        self.assertNotEqual(res.status_code, 200)


class PrivateManufacturerTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test123",
        )
        self.client.force_login(self.user)

    def test_retrieve_manufacturers(self):
        Manufacturer.objects.create(name="Tesla")
        Manufacturer.objects.create(name="BMW")
        response = self.client.get(MANUFACTURER_URL)
        self.assertEqual(response.status_code, 200)
        manufacturers = Manufacturer.objects.all()
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")


class PrivateDriverTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test",
            password="password123",
        )
        self.client.force_login(self.user)

    def test_create_driver(self):
        form_data = {
            "username": "new_driver",
            "password1": "user11test",
            "password2": "user11test",
            "first_name": "Test first",
            "last_name": "Test last",
            "license_number": "AVC12345",
        }
        self.client.post(reverse("taxi:driver-create"), data=form_data)
        new_user = get_user_model().objects.get(
            username=form_data["username"]
        )
        self.assertEqual(new_user.first_name, form_data["first_name"])
        self.assertEqual(new_user.last_name, form_data["last_name"])
        self.assertEqual(new_user.license_number, form_data["license_number"])


class DriverSearchTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="Alice",
            password="user123",
            license_number="AVC12345",
        )
        self.client.force_login(self.user)

        self.driver1 = get_user_model().objects.create_user(
            username="Bob",
            password="test123",
            license_number="ABC54321",
        )
        self.driver2 = get_user_model().objects.create_user(
            username="John",
            password="test321",
            license_number="CDA23456",
        )

    def test_search_finds_correct_driver(self):
        res = self.client.get(
            reverse("taxi:driver-list"),
            data={"username": self.driver1.username}
        )
        self.assertContains(res, self.driver1.username)

    def test_search_excludes_other_drivers(self):
        res = self.client.get(
            reverse("taxi:driver-list"),
            data={"username": self.driver1.username}
        )
        self.assertNotContains(res, self.driver2.username)

    def test_empty_search_returns_all(self):
        res = self.client.get(reverse("taxi:driver-list"))
        self.assertEqual(
            len(res.context["driver_list"]),
            len(get_user_model().objects.all())
        )


class CarSearchTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="Nick",
            password="user123",
            license_number="SSD12345",
        )
        self.client.force_login(self.user)
        self.manufacturer = Manufacturer.objects.create(
            name="Toyota",
            country="Japan"
        )
        self.car1 = Car.objects.create(
            model="Camry",
            manufacturer=self.manufacturer,
        )
        self.car2 = Car.objects.create(
            model="Corolla",
            manufacturer=self.manufacturer,
        )

    def test_search_finds_correct_car(self):
        res = self.client.get(
            reverse("taxi:car-list"),
            data={"model": self.car1.model}
        )
        self.assertContains(res, self.car1.model)

    def test_search_excludes_other_cars(self):
        res = self.client.get(
            reverse("taxi:car-list"),
            data={"model": self.car1.model}
        )
        self.assertNotContains(res, self.car2.model)

    def test_empty_search_returns_all(self):
        res = self.client.get(reverse("taxi:car-list"))
        self.assertEqual(
            len(res.context["car_list"]),
            len(Car.objects.all())
        )


class ManufacturerSearchTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="John",
            password="user123",
            license_number="EEW12345",
        )
        self.client.force_login(self.user)
        self.manufacturer1 = Manufacturer.objects.create(
            name="Tesla",
            country="USA"
        )
        self.manufacturer2 = Manufacturer.objects.create(
            name="Toyota",
            country="Japan"
        )

    def test_search_finds_correct_manufacturer(self):
        res = self.client.get(
            reverse("taxi:manufacturer-list"),
            data={"name": self.manufacturer1.name}
        )
        self.assertContains(res, self.manufacturer1.name)

    def test_search_excludes_other_manufacturers(self):
        res = self.client.get(
            reverse("taxi:manufacturer-list"),
            data={"name": self.manufacturer1.name}
        )
        self.assertNotContains(res, self.manufacturer2.name)

    def test_empty_search_returns_all(self):
        res = self.client.get(reverse("taxi:manufacturer-list"))
        self.assertEqual(
            len(res.context["manufacturer_list"]),
            len(Manufacturer.objects.all())
        )
