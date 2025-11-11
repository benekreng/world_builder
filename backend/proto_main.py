import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

# LangChain Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv


load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="SVG Generator API",
    description="Generates SVG visualizations from text using LangChain and an LLM."
)

# Configure CORS to allow React client (assuming it runs on localhost:3000)
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models for Request and LLM Output

# helpful in case Frontend post json
#class TextRequest(BaseModel):
#    """Schema for the incoming request from the React client."""
#    text: str = Field(..., description="The input text to be visualized.")


class SvgOutput(BaseModel):
    """Schema for forcing the LLM to produce a valid SVG."""
    svg_data: str = Field(..., description="A single string containing the complete, well-formed SVG code.")


# LangChain Component Initialization

# Check for API Key
if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

# Initialize the Chat Model (Using async method ainvoke for non-streaming)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# Initialize the Pydantic Output Parser
parser = PydanticOutputParser(pydantic_object=SvgOutput)

# Define the Prompt Template
SYSTEM_PROMPT = (
    "You are an expert visualization AI. Your task is to generate a simple, "
    "well-formed, and semantic SVG visualization based on the user's text input. "
    "Do not include any text outside of the SVG code. Your output must strictly "
    "adhere to the provided JSON schema. Ensure the SVG is valid XML."
    "\n\n{format_instructions}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Visualize this text: {request}"),
])

# Create the LangChain Runnable
visualization_chain = (
    {
        "request": lambda x: x["request"],
        "format_instructions": lambda _: parser.get_format_instructions(),
    }
    | prompt
    | llm
    | parser
)


# FastAPI Endpoint

@app.get("/generate-svg", response_class=Response)
async def generate_svg(request: str):
    """
    Receives text, calls the async LangChain pipeline to get SVG,
    and returns the SVG with the 'image/svg+xml' media type.
    """
    try:
        # Asynchronously invoke the LangChain chain
        # The chain returns a Pydantic object (SvgOutput)
        print(request)  #test
        result: SvgOutput = await visualization_chain.ainvoke({"request": request})

        # Extract the SVG string from the Pydantic model
        svg_content = result.svg_data

        # Return the SVG content directly with the correct media type
        return Response(content=svg_content, media_type="image/svg+xml")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Raise an HTTPException on failure
        raise HTTPException(
            status_code=500,
            detail=f"Error generating SVG: {str(e)}"
        )

# Server Run Command
# To start the server, run the following command in your terminal:
# uvicorn main:app --reload