import os
import sys
import unittest
import json

# Ensure parent directory is in path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
import database


class EcoProtectAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key_environment_protection'
        cls.client = app.test_client()

    def test_01_database_initialization(self):
        """Test database table creation and connectivity"""
        database.init_db()
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.assertIn('users', tables)
        self.assertIn('pledges', tables)
        self.assertIn('events', tables)

    def test_02_home_page(self):
        """Test index/home page loads with 200 OK"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'EcoProtect', response.data)

    def test_03_globe_page(self):
        """Test 3D Globe Observation Center loads with procedural Earth & HUD elements"""
        response = self.client.get('/globe')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        
        # Verify essential DOM containers for procedural Earth, pointers, and ledgers
        self.assertIn('globe-3d-canvas', content)
        self.assertIn('hud-top-bar', content)
        self.assertIn('left-dock', content)
        self.assertIn('createProceduralEarthTexture', content)

    def test_04_environmental_suites(self):
        """Test all core environmental and awareness module routes"""
        routes = [
            '/climate',
            '/forests',
            '/renewable-energy',
            '/water-conservation',
            '/waste-management',
            '/lifestyle',
            '/biodiversity',
            '/problems',
            '/solutions',
            '/about',
            '/contact',
            '/pledge',
            '/events',
            '/news',
            '/calculator'
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(
                    response.status_code, 200,
                    f"Route {route} failed with status {response.status_code}"
                )

    def test_05_api_hazards_endpoints(self):
        """Test crisis hazards REST APIs"""
        # Test hazard detail API
        res = self.client.get('/api/hazard/1')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('name', data)
        self.assertIn('deaths', data)

        # Test hazards list query API
        res_list = self.client.get('/api/hazards?year=1995')
        self.assertEqual(res_list.status_code, 200)
        hazards = json.loads(res_list.data)
        self.assertIsInstance(hazards, list)

    def test_06_scientific_carbon_calculator_api(self):
        """Test scientific carbon footprint calculation API"""
        payload = {
            'type': 'carbon',
            'electricity_kwh': 300,
            'gas_therms': 25,
            'car_km': 120,
            'vehicle_type': 'petrol',
            'transit_km': 40,
            'flights_short': 2,
            'flights_long': 1,
            'diet_type': 'average',
            'waste_bags': 2,
            'recycling_rate': 0.4,
            'household_members': 2
        }
        res = self.client.post('/api/calculate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('total_tonnes', data)
        self.assertIn('trees_needed', data)

    def test_07_scientific_water_calculator_api(self):
        """Test water conservation footprint calculation API"""
        payload = {
            'type': 'water',
            'shower_minutes': 6,
            'toilet_flushes': 4,
            'laundry_loads': 2,
            'dish_loads': 4,
            'garden_mins': 10,
            'low_flow': 'true',
            'household_size': 2
        }
        res = self.client.post('/api/calculate', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data.get('status'), 'success')
        self.assertIn('daily_liters_total', data)

    def test_08_vercel_entrypoint(self):
        """Test that api.index exports a valid WSGI callable for Vercel"""
        import api.index
        self.assertTrue(hasattr(api.index, 'app'))
        self.assertTrue(hasattr(api.index, 'application'))
        self.assertEqual(api.index.app, app)


if __name__ == '__main__':
    unittest.main()
