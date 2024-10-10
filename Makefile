default:
	python3 app.py& streamlit run frontend.py

docker-build-frontend:
	docker buildx build --platform linux/amd64 -t gcr.io/hardy-tine-435523-b0/frontend -f dockerfile-frontend  .

docker-build-backend:
	docker buildx build --platform linux/amd64 -t gcr.io/hardy-tine-435523-b0/backend -f dockerfile-backend  .

docker-build: docker-build-frontend docker-build-backend

docker-push:
	 docker push gcr.io/hardy-tine-435523-b0/frontend
	 docker push gcr.io/hardy-tine-435523-b0/backend

docker-all: docker-build docker-push

k8s-clean:
	kubectl delete -n backend deployment backend-deployment
	kubectl delete -n frontend deployment frontend-deployment

k8s-apply:
	kubectl apply -f k8s.yaml

k8s-show:
	kubectl get all -n frontend
	kubectl get all -n backend
