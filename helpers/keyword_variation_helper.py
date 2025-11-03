# helpers/keyword_variation_helper.py

import random
import string

class KeywordVariationHelper:
    """
    Helper để tạo keyword variations với 3 components:
    - K0: Original keyword (70% giữ nguyên, 30% combine)
    - K1: Suffix/Prefix từ list (30% có, random pick 1 value, random before/after K0)
    - K2: Random characters (30% có, random before/after K0, nhưng K1 luôn liền kề K0)
    """
    
    @staticmethod
    def parse_suffix_prefix_list(suffix_prefix_string):
        """
        Parse suffix_prefix string thành list
        
        Args:
            suffix_prefix_string: "watch, how to, video, tutorial"
        
        Returns:
            list: ['watch', 'how to', 'video', 'tutorial']
        """
        if not suffix_prefix_string or not suffix_prefix_string.strip():
            return []
        
        # Split by comma và strip spaces
        items = [item.strip() for item in suffix_prefix_string.split(';') if item.strip()]
        return items
    
    @staticmethod
    def generate_keyword_variation(original_keyword, suffix_prefix_list):
        """
        Generate keyword variation với logic:
        - 70% trả về K0 nguyên bản
        - 30% combine K0 với K1 và/hoặc K2
        
        Args:
            original_keyword: Keyword gốc (K0)
            suffix_prefix_list: List các suffix/prefix (K1 candidates)
        
        Returns:
            str: Final keyword variation
        """
        # 50% return original keyword
        if random.random() < 0.5:
            return original_keyword
        
        # 50% combine với K1 và/hoặc K2
        K0 = original_keyword
        
        # ========== GENERATE K1 (Random pick 1 từ list) ==========
        K1 = None
        if suffix_prefix_list:
            # 50% chance to use K1
            if random.random() < 0.5:
                K1 = random.choice(suffix_prefix_list)
        
        # ========== GENERATE K2 (Random characters) ==========
        K2 = None
        # 50% chance to use K2
        if random.random() < 0.5:
            K2 = KeywordVariationHelper._generate_random_string()
        
        # ========== COMBINE K0, K1, K2 ==========
        # Rule: K1 LUÔN LIỀN KỀ K0 (không bị K2 chen vào giữa)
        
        if K1 is None and K2 is None:
            # Cả 2 đều không có → trả về K0
            return K0
        
        elif K1 is not None and K2 is None:
            # Chỉ có K1 → Random K1 trước hoặc sau K0
            if random.random() < 0.5:
                return f"{K1} {K0}"  # K1 K0
            else:
                return f"{K0} {K1}"  # K0 K1
        
        elif K1 is None and K2 is not None:
            # Chỉ có K2 → Random K2 trước hoặc sau K0
            if random.random() < 0.5:
                return f"{K2} {K0}"  # K2 K0
            else:
                return f"{K0} {K2}"  # K0 K2
        
        else:
            # Có cả K1 và K2 → 4 combinations có thể
            # K1 luôn liền kề K0, K2 có thể ở đầu hoặc cuối
            
            combinations = [
                f"{K1} {K0} {K2}",  # K1 K0 K2
                f"{K2} {K1} {K0}",  # K2 K1 K0
                f"{K2} {K0} {K1}",  # K2 K0 K1
                f"{K0} {K1} {K2}",  # K0 K1 K2
            ]
            
            return random.choice(combinations)
    
    @staticmethod
    def _generate_random_string():
        """
        Generate random string: chữ, số, ký tự đặc biệt, space
        Length: 3-9 characters
        
        Returns:
            str: Random string
        """
        length = random.randint(3, 5)
        
        # Random chọn characters
        result = []
        for _ in range(length):
            # 70% chữ/số, 20% space, 10% ký tự đặc biệt
            rand = random.random()
            if rand < 0.7:
                result.append(random.choice(string.ascii_lowercase + string.digits))
            elif rand < 0.9:
                result.append(' ')
            else:
                result.append(random.choice("-_."))
        
        return ''.join(result).strip()  # Remove leading/trailing spaces
