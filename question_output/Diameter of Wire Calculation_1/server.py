import random
import math

def generate_problem():
    data = {'params': {}, 'correct_answers': {}}

    # 1. Dynamic Parameter Selection:
    # For simplicity, we'll use the SI unit system (N for force and MPa for stress).
    unitsForce = 'N'  # Newtons
    unitsStress = 'MPa'  # Megapascals

    # 2. Appropriate Transformations:
    # Stress in MPa will be converted to Pa in calculations to maintain SI unit consistency.

    # 3. Value Generation:
    # Generate random tensile force between 50 N and 70 N
    tensileForce = random.randint(50, 70)
    # Generate random stress between 2.5 MPa and 3.5 MPa
    stress = random.uniform(2.5, 3.5)

    # Store generated values in the data dictionary
    data['params']['tensileForce'] = tensileForce
    data['params']['unitsForce'] = unitsForce
    data['params']['stress'] = round(stress, 2)  # Round to 2 decimal places for readability
    data['params']['unitsStress'] = unitsStress

    # 4. Solution Synthesis:
    # Convert stress from MPa to Pa for calculation
    stress_pa = stress * 1e6  # 1 MPa = 1e6 Pa

    # Calculate the cross-sectional area A using the formula A = F / σ
    A = tensileForce / stress_pa  # in m^2

    # Solve for the diameter d using the area of a circle formula A = πd^2/4
    d_squared = A * 4 / math.pi
    diameter = math.sqrt(d_squared) * 1000  # Convert from m to mm

    # Store the calculated diameter in the data dictionary
    data['correct_answers']['diameter'] = round(diameter, 3)  # Round to 3 decimal places for precision

    return data

# Example usage
problem_data = generate_problem()
print(problem_data)