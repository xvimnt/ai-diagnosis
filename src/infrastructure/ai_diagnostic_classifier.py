import os
import json
from typing import List, Dict, Any
import openai

class AIDiagnosticClassifier:
    """Service for classifying network diagnostics using AI."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        openai.api_key = self.api_key
        
        # Initialize diagnostic categories with their validation prompts
        self.diagnostic_rules = {
            1: {
                "name": "Puerto LAN",
                "description": "Determina si existe una falla real que pueda ser atribuida a la caída de un equipo UNI, basada en la cantidad de errores encontrados, el estado de las interfaces y la información de los equipos UNI.",
                "prompt":  """
                    Determinar si existe una falla real que pueda ser atribuida a la caída de un equipo UNI, basada en la cantidad de errores encontrados, el estado de las interfaces y la información de los equipos UNI.

                    🔍 Condición 1: Validación de errores de interface
                    Verifica la cantidad total de errores encontrados en la lista de errores del proceso de revisión.

                    Compara ese número con el valor ""interface_details_error_count"".

                    Si ambos coinciden:

                    Revisa si existen equipos UNI.

                    Si un equipo UNI coincide con un equipo que tiene la interfaz en estado ""Down"", entonces:

                    Resultado: ""Diagnóstico confirmado: fallo relacionado con equipos UNI e interfaces caídas.""

                    🔍 Condición 2: Validación combinada de errores y coincidencia de hostnames
                    Suma los errores de ""interface"" y ""alarmas_sfp"" del proceso de revisión.

                    Compara esta suma con la cantidad de errores detectados.

                    Si coinciden:

                    Revisa la lista de equipos UNI caídos (""uni_downs"").

                    Verifica si alguno de sus ""hostnames"" coincide con los de los equipos reportados como con errores.

                    Si hay coincidencia:

                    Resultado: ""Diagnóstico confirmado: equipos UNI con errores críticos.""

                    🔍 Condición 3: Validación de UNI con errores activos
                    Revisa si el equipo UNI está marcado como ""caído"" y presenta errores en la revisión.

                    Si ambas condiciones se cumplen:

                    Resultado: ""Diagnóstico confirmado: UNI presenta errores y está fuera de servicio.""
                """
            },
            2: {
                "name": "Servicio Ok",
                "description": "Determina si el servicio está activo y en buen estado, verificando que no hayan errores en el detalle, que el servicio sea de tipo 'capacidad' o 'internet', que haya datos esenciales y que los equipos UNI estén configurados correctamente.",
                "prompt": """
                Determinar si existe una falla real que pueda ser atribuida a la caída de un equipo UNI, basada en la cantidad de errores encontrados, el estado de las interfaces y la información de los equipos UNI.

                🔍 Condición 1: Validación de errores de interface
                Verifica la cantidad total de errores encontrados en la lista de errores del proceso de revisión.

                Compara ese número con el valor ""interface_details_error_count"".

                Si ambos coinciden:

                Revisa si existen equipos UNI.

                Si un equipo UNI coincide con un equipo que tiene la interfaz en estado ""Down"", entonces:

                Resultado: ""Diagnóstico confirmado: fallo relacionado con equipos UNI e interfaces caídas.""

                🔍 Condición 2: Validación combinada de errores y coincidencia de hostnames
                Suma los errores de ""interface"" y ""alarmas_sfp"" del proceso de revisión.

                Compara esta suma con la cantidad de errores detectados.

                Si coinciden:

                Revisa la lista de equipos UNI caídos (""uni_downs"").

                Verifica si alguno de sus ""hostnames"" coincide con los de los equipos reportados como con errores.

                Si hay coincidencia:

                Resultado: ""Diagnóstico confirmado: equipos UNI con errores críticos.""

                🔍 Condición 3: Validación de UNI con errores activos
                Revisa si el equipo UNI está marcado como ""caído"" y presenta errores en la revisión.

                Si ambas condiciones se cumplen:

                Resultado: Diagnóstico confirmado: UNI presenta errores y está fuera de servicio.
            """
            },
            3: {
                "name": "Energía Cliente",
                "description": "Determina si el servicio está activo y en buen estado, verificando que no haya errores en el detalle, que el servicio sea de tipo 'capacidad' o 'internet', que haya datos esenciales y que los equipos UNI estén configurados correctamente.",
                "prompt": """
                    "✅ Condiciones para considerar que el servicio está OK:
                    Sin errores en el detalle:

                    Verifica que no existan errores en la sección ""detail"" del proceso de revisión.

                    Tipo de servicio:

                    Asegúrate de que el servicio sea de tipo ""capacidad"" o ""internet"".

                    Presencia de datos esenciales:

                    Confirma que existan equipos UNI asociados.

                    Valida que exista una dirección MAC.

                    Validación de equipos UNI:

                    Cada equipo UNI debe tener en su interfaz de descripción la palabra ""UNI"".

                    Los hostnames de los equipos deben coincidir entre la sección UNI y los detalles del equipo analizado.

                    Cascada sin errores:

                    Si el equipo está en una arquitectura de ""cascada"" y no presenta errores en los UNI, también se considera válido si hay equipos UNI y una MAC address.

                    📌 Regla de decisión final:
                    Si todas las condiciones anteriores se cumplen, o si el equipo está en cascada y cumple con el punto 5:

                    Resultado: "Diagnóstico confirmado: servicio activo y en buen estado."

                    Si alguna condición falla:

                    Resultado: "Diagnóstico no confirmado: revisar inconsistencias en la configuración del servicio.""
                """
            },
        }
    
    async def _validate_diagnostic_prompt(self, category_id: int, diagnostic_input: Dict[str, Any]) -> bool:
        """Validate if the diagnostic input matches the category's validation prompt."""
        steps = diagnostic_input.get("steps", [])
        formatted_steps = [f"Step: {step['step']}\nResult: {step['result']}" for step in steps]
        steps_text = "\n\n".join(formatted_steps)
        validation_prompt = f"""You are a network diagnostic validator. Given these diagnostic steps and results:
{steps_text}

Validate if they match this diagnostic pattern:
{self.diagnostic_rules[category_id]['prompt']}

Respond with 'true' if it matches, 'false' if it doesn't. Only respond with true/false."""

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a network diagnostic validation assistant."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0
            )
            return response.choices[0].message.content.strip().lower() == "true"
        except Exception as e:
            print(f"Error validating diagnostic: {str(e)}")
            return False

    async def classify_diagnostic(self, diagnostic_input: Dict[str, Any]) -> int:
        """Analyze diagnostic input and determine the most appropriate category.
        First selects potential categories, then validates them until finding a match."""
        steps = diagnostic_input.get("steps", [])
        formatted_steps = [f"Step: {step['step']}\nResult: {step['result']}" for step in steps]
        steps_text = "\n\n".join(formatted_steps)

        # First, get potential categories
        categories_str = "\n".join(
            f"{id}: {rule['name']}\nDescription: {rule['description']}"
            for id, rule in self.diagnostic_rules.items()
        )

        selection_prompt = f"""You are a network diagnostic classifier. Given these diagnostic steps:
        {steps_text}

        Select the most likely diagnostic categories from this list, ordered by likelihood:
        {categories_str}

        Respond with only the category IDs separated by commas (e.g., '1,2,3')."""

        try:
            # Get initial category suggestions
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a network diagnostic classification assistant."},
                    {"role": "user", "content": selection_prompt}
                ],
                temperature=0
            )
            
            # Parse the comma-separated category IDs
            potential_categories = [int(id.strip()) for id in response.choices[0].message.content.split(',')]
            print(f"Potential categories identified: {potential_categories}")
            
            # Try each suggested category in order
            for category_id in potential_categories:
                if category_id not in self.diagnostic_rules:
                    continue
                    
                print(f"Validating category {category_id}: {self.diagnostic_rules[category_id]['name']}")
                if await self._validate_diagnostic_prompt(category_id, diagnostic_input):
                    print(f"Found matching category: {category_id}")
                    return category_id
                    
            # If no categories match or an error occurs, return Undetermined (8)
            print("No matching categories found, defaulting to Undetermined")
            return 8
            
        except Exception as e:
            print(f"Error in classification process: {str(e)}")
            return 8
