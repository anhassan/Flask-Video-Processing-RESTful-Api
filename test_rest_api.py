import unittest
import requests
from app import db, VideoInstance


class TestVideoRestApi(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:5000/media/videos/"
    videos_content = [{"name": "How to Cook??", "views": 1000, "likes": 250},
                      {"name": "Learn to Code", "views": 12345, "likes": 2456},
                      {"name": "What is the purpose of life", "views": 7895, "likes": 2867}]
    expected_video_resposnes = []
    for video_id, content in enumerate(videos_content):
        videos_content[video_id]["id"] = video_id
        expected_video_resposnes.append(videos_content[video_id])

    def setUp(self):
        for video_id, content in enumerate(self.videos_content):
            requests.put(self.BASE_URL + str(video_id), content)
        db.session.commit()

    def tearDown(self):
        db.session.query(VideoInstance).delete()
        db.session.commit()

    def test_get(self):
        actual_get_responses = []
        for index in range(0, 3):
            response = (requests.get(self.BASE_URL + str(index)))
            actual_get_responses.append(response.json())
        self.assertEqual(actual_get_responses, self.expected_video_resposnes)

    def test_put(self):
        expected_put_response = {"name": "Patience is the key", "views": 1432, "likes": 534}
        resposne = requests.put(self.BASE_URL + "3", expected_put_response)
        expected_put_response["id"] = 3
        actual_put_response = requests.get(self.BASE_URL + str(expected_put_response["id"]))
        self.assertEqual(actual_put_response.json(), expected_put_response)

    def test_patch(self):
        requests.patch(self.BASE_URL + "0", {"views": "1342"})
        expected_patch_response = self.expected_video_resposnes[0]
        expected_patch_response["views"] = 1342
        actual_patch_response = requests.get(self.BASE_URL + "0")
        self.assertEqual(actual_patch_response.json(), expected_patch_response)

    def test_delete(self):
        response = requests.delete(self.BASE_URL + "0")
        video_deleted_actual = VideoInstance.query.filter_by(id=0).first()
        self.assertEqual(response.json(), self.expected_video_resposnes[0])
        self.assertEqual(video_deleted_actual, None)

    def test_exceptions(self):
        msg_not_found = "Not Found : Video with video id {} is not found".format(4)
        msg_already_exists = "Already Exists : Video with video id {} already exists".format(0)

        expected_response_not_found = {'message': msg_not_found}
        expected_response_already_exists = {'message': msg_already_exists}

        url_not_found = self.BASE_URL + "4"
        url_already_exists = self.BASE_URL + "0"

        actual_response_get = requests.get(url_not_found).json()
        actual_response_patch = requests.patch(url_not_found).json()
        actual_response_delete = requests.delete(url_not_found).json()
        actual_response_put = requests.put(url_already_exists, self.videos_content[0]).json()

        self.assertEqual(actual_response_get, expected_response_not_found)
        self.assertEqual(actual_response_patch, expected_response_not_found)
        self.assertEqual(actual_response_delete, expected_response_not_found)
        self.assertEqual(actual_response_put, expected_response_already_exists)


if __name__ == '__main__':
    unittest.main()
