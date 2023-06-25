vision:
	docker run -p 8000:8000 charlie-vision

artifact-push:
	docker push asia-southeast1-docker.pkg.dev/the-lazy-lawyer/charlie-vision-docker/charlie-vision:latest

artifact-tag:
	docker tag charlie-vision asia-southeast1-docker.pkg.dev/the-lazy-lawyer/charlie-vision-docker/charlie-vision:latest
