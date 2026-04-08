"""Roadmap API — Generate and manage learning paths."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.roadmap import RoadmapRequest, RoadmapResponse, ModuleSchema, TopicSchema
from app.agents.roadmap import roadmap_agent
from app.models.roadmap import Roadmap, RoadmapModule, RoadmapTopic
from app.models.user import User

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(request: RoadmapRequest, db: AsyncSession = Depends(get_db)):
    """Generate a personalized learning roadmap."""
    # Generate roadmap from agent
    roadmap_data = roadmap_agent.generate(request.goal)

    # Save to DB
    roadmap = Roadmap(
        user_id=request.user_id,
        goal=request.goal,
        timeframe=request.timeframe,
    )
    db.add(roadmap)
    await db.flush()

    # Update user goal
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    if user:
        user.current_goal = request.goal

    modules_response = []
    for mod_data in roadmap_data["modules"]:
        module = RoadmapModule(
            roadmap_id=roadmap.id,
            title=mod_data["title"],
            description=mod_data["description"],
            order=mod_data["order"],
            status=mod_data["status"],
            estimated_hours=mod_data["estimated_hours"],
        )
        db.add(module)
        await db.flush()

        topics_response = []
        for topic_data in mod_data["topics"]:
            topic = RoadmapTopic(
                module_id=module.id,
                title=topic_data["title"],
                description=topic_data["description"],
                order=topic_data["order"],
                status=topic_data["status"],
                difficulty=topic_data["difficulty"],
                xp_reward=topic_data["xp_reward"],
            )
            db.add(topic)
            topics_response.append(TopicSchema(**topic_data))

        modules_response.append(ModuleSchema(
            id=module.id,
            title=mod_data["title"],
            description=mod_data["description"],
            order=mod_data["order"],
            status=mod_data["status"],
            progress=0.0,
            estimated_hours=mod_data["estimated_hours"],
            topics=topics_response,
        ))

    return RoadmapResponse(
        id=roadmap.id,
        goal=request.goal,
        timeframe=request.timeframe,
        modules=modules_response,
    )


@router.get("/{user_id}", response_model=RoadmapResponse | None)
async def get_roadmap(user_id: int, db: AsyncSession = Depends(get_db)):
    """Get the active roadmap for a user."""
    result = await db.execute(
        select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
        .order_by(Roadmap.created_at.desc())
    )
    roadmap = result.scalar_one_or_none()
    if not roadmap:
        return None

    # Load modules and topics
    modules_result = await db.execute(
        select(RoadmapModule).where(RoadmapModule.roadmap_id == roadmap.id)
        .order_by(RoadmapModule.order)
    )
    modules = modules_result.scalars().all()

    modules_response = []
    for module in modules:
        topics_result = await db.execute(
            select(RoadmapTopic).where(RoadmapTopic.module_id == module.id)
            .order_by(RoadmapTopic.order)
        )
        topics = topics_result.scalars().all()

        modules_response.append(ModuleSchema(
            id=module.id,
            title=module.title,
            description=module.description or "",
            order=module.order,
            status=module.status,
            progress=module.progress,
            estimated_hours=module.estimated_hours,
            topics=[TopicSchema(
                id=t.id,
                title=t.title,
                description=t.description or "",
                order=t.order,
                status=t.status,
                difficulty=t.difficulty,
                xp_reward=t.xp_reward,
            ) for t in topics]
        ))

    overall = 0
    if modules_response:
        overall = sum(m.progress for m in modules_response) / len(modules_response)

    return RoadmapResponse(
        id=roadmap.id,
        goal=roadmap.goal,
        timeframe=roadmap.timeframe,
        status=roadmap.status,
        overall_progress=overall,
        modules=modules_response,
    )
