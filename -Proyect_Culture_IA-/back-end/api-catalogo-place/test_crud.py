import json
import urllib.request
import urllib.error

def test_crud():
    base_url = 'http://127.0.0.1:8001'

    # Test 1: Crear un lugar (CREATE)
    print("=== TEST 1: CREATE ===")
    place_data = {
        'name': 'Museo del Prado',
        'description': 'Museo de arte español',
        'category': 'Museo',
        'latitude': 40.4138,
        'longitude': -3.6921
    }

    try:
        req = urllib.request.Request(
            f'{base_url}/places/',
            data=json.dumps(place_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            place_id = result['id']
            print(f"✅ Lugar creado con ID: {place_id}")
            print(f"Respuesta: {result}")
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP: {e.code} - {e.read().decode('utf-8')}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # Test 2: Listar lugares (READ ALL)
    print("\n=== TEST 2: READ ALL ===")
    try:
        with urllib.request.urlopen(f'{base_url}/places/') as response:
            places = json.loads(response.read().decode('utf-8'))
            print(f"✅ Lugares encontrados: {len(places)}")
            for place in places:
                print(f"  - {place['name']} (ID: {place['id']})")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Obtener lugar por ID (READ ONE)
    print(f"\n=== TEST 3: READ ONE (ID: {place_id}) ===")
    try:
        with urllib.request.urlopen(f'{base_url}/places/{place_id}') as response:
            place = json.loads(response.read().decode('utf-8'))
            print(f"✅ Lugar encontrado: {place['name']}")
            print(f"Descripción: {place['description']}")
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4: Actualizar lugar (UPDATE)
    print(f"\n=== TEST 4: UPDATE (ID: {place_id}) ===")
    update_data = {
        'description': 'Museo de arte español - Actualizado',
        'importance_score': 0.95
    }
    try:
        req = urllib.request.Request(
            f'{base_url}/places/{place_id}',
            data=json.dumps(update_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='PATCH'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Lugar actualizado: {result['name']}")
            print(f"Nueva descripción: {result['description']}")
            print(f"Nuevo score: {result['importance_score']}")
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 5: Eliminar lugar (DELETE)
    print(f"\n=== TEST 5: DELETE (ID: {place_id}) ===")
    try:
        req = urllib.request.Request(
            f'{base_url}/places/{place_id}',
            method='DELETE'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✅ Lugar eliminado: {result['detail']}")
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 6: Verificar que el lugar ya no existe
    print(f"\n=== TEST 6: VERIFY DELETION (ID: {place_id}) ===")
    try:
        with urllib.request.urlopen(f'{base_url}/places/{place_id}') as response:
            print("❌ El lugar aún existe (debería haber sido eliminado)")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✅ Lugar correctamente eliminado (404 esperado)")
        else:
            print(f"❌ Error inesperado: {e.code}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_crud()