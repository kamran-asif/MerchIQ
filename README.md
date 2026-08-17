# MerchIQ

MerchIQ is a full-stack retail analytics application with a FastAPI backend and a Vite + React frontend.

Contents
- `backend/` — FastAPI backend, services, and APIs
- `frontend/` — Vite + React UI and components
- `docker-compose.yml` — local dev stack for backend + frontend

Quick start (development)

1. Backend (Python)

	 - Create and activate a virtual environment:

		 ```powershell
		 python -m venv .venv
		 .\.venv\Scripts\Activate.ps1
		 pip install -r backend/requirements.txt
		 ```

	 - Run the FastAPI app:

		 ```powershell
		 cd backend
		 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
		 ```

2. Frontend (development)

	 - Install dependencies and start Vite dev server:

		 ```powershell
		 cd frontend
		 npm install
		 npm run dev
		 ```

3. Using Docker

	 - Start the full stack with Docker Compose:

		 ```powershell
		 docker-compose up --build
		 ```

Testing

- Python tests (if any):

	```powershell
	cd backend
	pytest
	```

Notes
- Environment variables should be set in a `.env` file in `backend/` when required.
- The `docker/` folder contains auxiliary Docker configs.

Contributing

- Open an issue or create a PR. Keep changes focused and add tests where appropriate.

License

- Add a license file if you intend to open-source this repository.
