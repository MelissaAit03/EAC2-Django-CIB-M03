from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        opts = Options()
        opts.add_argument("-headless")
        cls.selenium = webdriver.Firefox(options=opts)
        cls.selenium.implicitly_wait(5)

        # Creem el superusuari inicial
        user = User.objects.create_user(
            "isard", "isard@isardvdi.com", "pirineus"
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_usermelissa_no_puede_acceder_admin(self):

        # Login del superusuari
        self.selenium.get(self.live_server_url + "/admin/")

        self.selenium.find_element(By.ID, "id_username").send_keys("isard")
        self.selenium.find_element(By.ID, "id_password").send_keys("pirineus")
        self.selenium.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        ).click()

        # Accedim a la llista d'usuaris
        self.selenium.find_element(
            By.XPATH, "//a[contains(@href, '/admin/auth/user/')]"
        ).click()

        # Obrim el formulari AFEGIR USUARI, no el d'afegir grup
        self.selenium.find_element(
            By.XPATH, "//a[contains(@href, '/admin/auth/user/add/')]"
        ).click()

        # Creem usermelissa mitjancant Selenium
        self.selenium.find_element(By.ID, "id_username").send_keys("usermelissa")
        self.selenium.find_element(By.ID, "id_password1").send_keys("Riu!Cactus47Brisa2026")
        self.selenium.find_element(By.ID, "id_password2").send_keys("Riu!Cactus47Brisa2026")

        self.selenium.find_element(By.NAME, "_save").click()


        # Comprovem que apareix a la llista d'usuaris
        self.selenium.get(self.live_server_url + "/admin/auth/user/")

        usuario = self.selenium.find_element(
            By.XPATH, "//a[normalize-space(text())='usermelissa']"
        )
        self.assertTrue(usuario.is_displayed())

        # Obrim la fitxa de l'usuari per comprovar els seus permisos
        usuario.click()

        self.assertFalse(
            self.selenium.find_element(By.ID, "id_is_staff").is_selected()
        )
        self.assertFalse(
            self.selenium.find_element(By.ID, "id_is_superuser").is_selected()
        )

        self.assertEqual(
            [],
            self.selenium.find_elements(
                By.CSS_SELECTOR, "#id_groups option:checked"
            )
        )

        self.assertEqual(
            [],
            self.selenium.find_elements(
                By.CSS_SELECTOR, "#id_user_permissions option:checked"
            )
        )

        # Tanquem la sessio de l'administrador
        self.selenium.find_element(
            By.CSS_SELECTOR, "#logout-form button"
        ).click()

        # Intentem entrar amb l'usuari normal
        self.selenium.get(self.live_server_url + "/admin/login/")

        self.selenium.find_element(By.ID, "id_username").send_keys("usermelissa")
        self.selenium.find_element(By.ID, "id_password").send_keys("Riu!Cactus47Brisa2026")
        self.selenium.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        ).click()

        # Intentem accedir de nou a l'administrador
        self.selenium.get(self.live_server_url + "/admin/")

        # Ha de continuar a la pantalla de login
        self.assertIn("/admin/login/", self.selenium.current_url)
        self.assertTrue(
            self.selenium.find_elements(By.ID, "login-form")
        )

        # Comprovem que NO existeix l'enllaç a la llista d'usuaris
        try:
            self.selenium.find_element(
                By.XPATH, "//a[contains(@href, '/admin/auth/user/')]"
            )
            self.fail("L'usuari normal ha pogut entrar a l'administrador")
        except NoSuchElementException:
            pass
