""" Server-to-Server OAuth認証によるZoomAPIからミーティングを作成するサンプル

参考URL
    https://marketplace.zoom.us/docs/guides/build/server-to-server-oauth-app/
    https://marketplace.zoom.us/docs/api-reference/zoom-api/methods/#operation/meetingCreate
"""

import json
from base64 import b64encode
from http import HTTPStatus

import requests


class ZoomAPI:
    """ ZoomAPIのラッパークラス

    Attributes:
        account_id (str): Account ID
        client_id (str): Client ID
        client_secret (str): Client secret
    """

    @classmethod
    def _get_token(cls):
        """アクセストークンを取得する

        ・Server to Server OAutu認証

        Returns:
            str: 取得したアクセストークン
        """

        url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={cls.account_id}"

        # HTTPヘッダーは特殊記号を使用できないのでClient IDとClient secretをBase64にエンコードする
        b64_client = f"{cls.client_id}:{cls.client_secret}".encode()
        b64_client = b64encode(b64_client).decode()
        headers = {"Authorization": f"Basic {b64_client}", }

        r = requests.post(url=url, headers=headers)
        if r.status_code == HTTPStatus.OK:
            return r.json()["access_token"]
        else:
            raise Exception("アクセストークンの取得に失敗しました。")

    @classmethod
    def create_meeting(cls, topic=None, start_time=None, duration=60):
        """ミーティングを作成する

        Args:
            topic (str, optional): ミーティングの議題
            start_time (str, optional): ミーティングの開始時刻(yyyy-MM-ddTHH:mm:ss形式)
            duration (int, optional): ミーティングの予定時間(分単位)　デフォルトは60分

        Returns:
            str: ミーティングのURL
        """

        # アクセストークンを取得する
        access_token = cls._get_token()

        # ミーティングを作成する
        url = "https://api.zoom.us/v2/users/me/meetings"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "topic": topic,
            "start_time": start_time,
            "duration": duration,
            "timezone": "Asia/Tokyo",
        }
        r = requests.post(url=url, headers=headers, data=json.dumps(payload))
        if r.status_code == HTTPStatus.CREATED:
            return r.json()["join_url"]
        else:
            raise Exception("ミーティングの作成に失敗しました。")


if __name__ == "__main__":

    # NOTE: ご自身で取得した「Account ID」「Client ID」「Client secret」を入力してください。
    ZoomAPI.account_id = "XXX"
    ZoomAPI.client_id = "XXX"
    ZoomAPI.client_secret = "XXX"

    try:
        topic = "サンプル会議"
        start_time = "2022-12-17T15:00:00"
        meeting_url = ZoomAPI.create_meeting(topic, start_time, 30)
        print(meeting_url)
    except Exception as e:
        print(e)
