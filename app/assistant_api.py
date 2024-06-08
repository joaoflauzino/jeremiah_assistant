from fastapi import FastAPI, HTTPException, status
import logging
from finance_agent.agent import send_message
import uvicorn
from fastapi.encoders import jsonable_encoder
from validation_schema.assistant.validate import Assistant
from fastapi.responses import PlainTextResponse


app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/assistant", status_code=status.HTTP_200_OK, response_class=PlainTextResponse)
def gemini_assistant(text: Assistant) -> str:
    try:
        transformed_text = jsonable_encoder(text)
        logger.info(f"Sending api request...")
        response = send_message(transformed_text["text"])
        return response
    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run("assistant_api:app", host="0.0.0.0", port=9000, reload=True, workers=1)
