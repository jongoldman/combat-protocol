import boto3
import json
import sys

class LikenessGuard:
    def __init__(self, region_name="us-east-1"):
        # Uses standard AWS credential chain (~/.aws/credentials)
        self.client = boto3.client('rekognition', region_name=region_name)

    def screen_image_for_celebrities(self, image_path):
        """
        Screens an exported character render for celebrity likeness.
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()

            response = self.client.recognize_celebrities(Image={'Bytes': image_bytes})
            
            flagged_celebs = []
            for celebrity in response.get('CelebrityFaces', []):
                # We flag if confidence is > 80%
                if celebrity['MatchConfidence'] > 80.0:
                    flagged_celebs.append({
                        "name": celebrity['Name'],
                        "confidence": celebrity['MatchConfidence'],
                        "info_url": celebrity.get('Urls', [None])[0]
                    })
            
            return flagged_celebs

        except Exception as e:
            print(f"Filter Error: {e}")
            return None

if __name__ == "__main__":
    # Integration example for your backend pipeline
    guard = LikenessGuard()
    # Assume 'render.png' is the current user's character screenshot
    results = guard.screen_image_for_celebrities("character_render.png")
    
    if results:
        print("⚠️ COMPLIANCE ALERT: Potential Likeness Violation Detected")
        print(json.dumps(results, indent=2))
        # Logic: Block upload or set 'license_status' to 'Pending'
    else:
        print("✅ No known celebrity likeness detected at high confidence.")


