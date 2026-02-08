def transl_p(input_text):
    return f'''Translate the following text into Russian word for word, preserving the exact original structure, punctuation, and wording as closely as possible.
    Do not interpret, paraphrase, restructure, summarize, or add anything. 
    Output only the translated text as a single continuous block with no extra characters, formatting, headings, explanations, or line breaks.
    Begin the response immediately with the first word of the translation.
    Input text:\n\n{input_text}
    '''
    
def summ_p(input_text):
    return f'''Summarize the following text concisely, reducing its length by 60–70% while preserving the core meaning, key facts, and essential details.
Maintain the original language of the input text.
Do not add any explanations, headings, disclaimers, or extra formatting.
Output only the summarized text as a single, clean paragraph with no markdown, special characters, or line breaks.
Begin the response immediately with the first word of the summary.
Text to summarize:\n\n{input_text}
'''
