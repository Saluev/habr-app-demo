import React, {Component} from 'react';
import {connect} from 'react-redux'
import {createSession} from '../redux/actions'
import Checkers from "./games/checkers";

class GamePage extends Component {

    componentDidMount() {
        this.props.dispatch(createSession())
    }

    render() {
        const {session, room} = this.props;
        const isLoading = !session || !room;
        return (
            <div>
                {isLoading && <h2>Loading...</h2>}
                {session && <p>Session: {session.id}</p>}
                {room && <p>Room: {JSON.stringify(room)}</p>}
                {room && room.kind === "checkers" && <Checkers/>}
            </div>
        );
    }
}

function mapStateToProps(state) {
    const {page} = state;
    return page;
}

export default connect(mapStateToProps)(GamePage);
