import os
 
class TemplateParser:

    # constructor
    def __init__(self, language: str= None, default_language:str = "en"):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_langauge = default_language
        self.language = language
    
    # set lanuage of template
    def set_language(self, language: str):
        if not language:
            self.language = self.default_langauge
            return None
        
        language_path = os.path.join(self.current_path, "locales", language)

        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_langauge
        
        return True
    
    def get(self, group: str, key: str, vars: dict = {}):
        
        if not group or not key:
            return None
        
        
        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py")
        targeted_language = self.language
        
        # check if group path exists
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_langauge, f"{group}.py")
            targeted_language = self.default_langauge

        if not os.path.exists(group_path):
            return None
        
        # import group
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])

        if not module:
            return None
        
        # get key
        key_attribute = getattr(module, key)
        return key_attribute.substitute(vars)