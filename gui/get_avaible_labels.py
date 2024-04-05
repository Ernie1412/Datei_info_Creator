from dataclasses import dataclass

@dataclass
class GetLabels():    
    
    def get_available_labels(self, main, label_name):
        label_count: int=0
        for idx in range(10):
            if hasattr(main, f"{label_name}{idx}"):
                label_count +=1
        return label_count
    
    def get_avaible_socialmedia_buttons(self, main, button_name):
        button_count: int=0
        for idx in range(10):
            if hasattr(main, f"{button_name}{idx}"):
                button_count +=1
        return button_count
    
if __name__ == '__main__':
    GetLabels()