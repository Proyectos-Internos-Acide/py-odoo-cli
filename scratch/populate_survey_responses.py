import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from odoo_cli import OdooClient

def main():
    client = OdooClient()
    client.connect()
    
    print("--- Connected to Odoo. Populating survey responses... ---")
    
    # 1. Find the survey ID (Encuesta de Satisfacción - Machu Picchu Exclusive Tours)
    surveys = client.search_read(
        'survey.survey',
        [('title', '=', "Encuesta de Satisfacción - Machu Picchu Exclusive Tours")],
        fields=['id']
    )
    if not surveys:
        print("⚠️ Error: Survey not found. Run create_tour_survey.py first.")
        return
    survey_id = surveys[0]['id']
    print(f"Found Survey ID: {survey_id}")

    # 2. Get questions and answer choices map dynamically
    questions = client.search_read('survey.question', [('survey_id', '=', survey_id)], fields=['id', 'title', 'question_type'])
    
    q_map = {}
    for q in questions:
        q_id = q['id']
        title = q['title']
        q_type = q['question_type']
        
        # If it's a choice question, retrieve the answer options
        answers_map = {}
        if q_type == 'simple_choice':
            answers = client.search_read('survey.question.answer', [('question_id', '=', q_id)], fields=['id', 'value'])
            for ans in answers:
                answers_map[ans['value']] = ans['id']
        
        q_map[title] = {
            'id': q_id,
            'type': q_type,
            'answers': answers_map
        }
    
    # 3. Find our clients
    clients = ["Emily Watson", "Hans Müller", "Lucas Silva"]
    partner_ids = {}
    for name in clients:
        exist = client.search_read('res.partner', [('name', '=', name)], fields=['id'])
        if exist:
            partner_ids[name] = exist[0]['id']
        else:
            partner_ids[name] = None
            print(f"⚠️ Warning: Client '{name}' not found. Answer will be anonymous.")

    # 4. Answers to inject
    responses_to_create = [
        {
            'client_name': "Emily Watson",
            'answers': [
                {
                    'question_title': "¿Cómo calificaría la amabilidad y conocimiento de su guía turístico?",
                    'type': 'simple_choice',
                    'val': "Excelente"
                },
                {
                    'question_title': "¿Cómo calificaría la puntualidad y la logística general del tour?",
                    'type': 'simple_choice',
                    'val': "Excelente"
                },
                {
                    'question_title': "¿El itinerario cubrió todas sus expectativas de viaje?",
                    'type': 'simple_choice',
                    'val': "Superó mis expectativas"
                },
                {
                    'question_title': "¿Qué tan probable es que recomiende Machu Picchu Exclusive Tours a sus amigos o familiares?",
                    'type': 'scale',
                    'val': 10
                },
                {
                    'question_title': "¿Tiene algún comentario adicional o sugerencia para mejorar nuestro servicio?",
                    'type': 'text_box',
                    'val': "An absolutely magical trip! Our guide was extremely knowledgeable, and the logistics were flawless."
                }
            ]
        },
        {
            'client_name': "Hans Müller",
            'answers': [
                {
                    'question_title': "¿Cómo calificaría la amabilidad y conocimiento de su guía turístico?",
                    'type': 'simple_choice',
                    'val': "Excelente"
                },
                {
                    'question_title': "¿Cómo calificaría la puntualidad y la logística general del tour?",
                    'type': 'simple_choice',
                    'val': "Bueno"
                },
                {
                    'question_title': "¿El itinerario cubrió todas sus expectativas de viaje?",
                    'type': 'simple_choice',
                    'val': "Cumplió todas"
                },
                {
                    'question_title': "¿Qué tan probable es que recomiende Machu Picchu Exclusive Tours a sus amigos o familiares?",
                    'type': 'scale',
                    'val': 9
                },
                {
                    'question_title': "¿Tiene algún comentario adicional o sugerencia para mejorar nuestro servicio?",
                    'type': 'text_box',
                    'val': "Very good experience. The Inca Trail trek was hard but rewarding. The guide paced the hike very well."
                }
            ]
        },
        {
            'client_name': "Lucas Silva",
            'answers': [
                {
                    'question_title': "¿Cómo calificaría la amabilidad y conocimiento de su guía turístico?",
                    'type': 'simple_choice',
                    'val': "Bueno"
                },
                {
                    'question_title': "¿Cómo calificaría la puntualidad y la logística general del tour?",
                    'type': 'simple_choice',
                    'val': "Excelente"
                },
                {
                    'question_title': "¿El itinerario cubrió todas sus expectativas de viaje?",
                    'type': 'simple_choice',
                    'val': "Cumplió la mayoría"
                },
                {
                    'question_title': "¿Qué tan probable es que recomiende Machu Picchu Exclusive Tours a sus amigos o familiares?",
                    'type': 'scale',
                    'val': 8
                },
                {
                    'question_title': "¿Tiene algún comentario adicional o sugerencia para mejorar nuestro servicio?",
                    'type': 'text_box',
                    'val': "Muito bom! O serviço foi muito bem organizado e a pontualidade excelente."
                }
            ]
        }
    ]

    # 5. Populate
    for resp in responses_to_create:
        c_name = resp['client_name']
        partner_id = partner_ids.get(c_name)
        
        # Create user input record
        input_vals = {
            'survey_id': survey_id,
            'state': 'done'
        }
        if partner_id:
            input_vals['partner_id'] = partner_id
            
        user_input_id = client.create('survey.user_input', input_vals)
        print(f"\nCreated User Input for {c_name} (ID: {user_input_id})")
        
        # Create user input lines (answers)
        for ans in resp['answers']:
            q_title = ans['question_title']
            q_info = q_map.get(q_title)
            if not q_info:
                # Try finding by loose match to handle encoding or slight variations
                matched_title = next((t for t in q_map.keys() if q_title in t or t in q_title), None)
                if matched_title:
                    q_info = q_map[matched_title]
                else:
                    print(f"⚠️ Warning: Question not found: '{q_title}'")
                    continue
            
            q_id = q_info['id']
            q_type = q_info['type']
            
            line_vals = {
                'user_input_id': user_input_id,
                'question_id': q_id,
                'survey_id': survey_id
            }
            
            if q_type == 'simple_choice':
                val_text = ans['val']
                ans_id = q_info['answers'].get(val_text)
                if ans_id:
                    line_vals.update({
                        'answer_type': 'suggestion',
                        'suggested_answer_id': ans_id
                    })
                else:
                    print(f"  ⚠️ Warning: Answer choice '{val_text}' not found for question '{q_title}'")
                    continue
            elif q_type == 'scale':
                line_vals.update({
                    'answer_type': 'numerical_box',
                    'value_numerical_box': float(ans['val'])
                })
            elif q_type == 'text_box':
                line_vals.update({
                    'answer_type': 'text_box',
                    'value_text_box': ans['val']
                })
            
            line_id = client.create('survey.user_input.line', line_vals)
            print(f"  Added answer to '{q_title[:30]}...' (Line ID: {line_id})")

    print("\n--- Survey responses population successfully finished! ---")

if __name__ == '__main__':
    main()
