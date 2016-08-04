package com.krumbs.getkrumbs.sdk.reachoapp;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;

import com.getbase.floatingactionbutton.FloatingActionButton;
import com.getbase.floatingactionbutton.FloatingActionsMenu;
import com.joanzapata.iconify.IconDrawable;
import com.joanzapata.iconify.Iconify;
import com.joanzapata.iconify.fonts.FontAwesomeIcons;
import com.joanzapata.iconify.fonts.FontAwesomeModule;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener {
    public static String FROM_TITLE = "com.krumbsreacho.sample.FromActionTitle";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Iconify.with(new FontAwesomeModule());

        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        final FloatingActionsMenu menuMultipleActions = (FloatingActionsMenu) findViewById(R.id.multiple_actions);

        configureActionsMenu(menuMultipleActions);


        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.setDrawerListener(toggle);
        toggle.syncState();


        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);
    }

    private class MyActionListener implements View.OnClickListener {

        private FloatingActionButton _myButton;
        public MyActionListener(FloatingActionButton b) {
            _myButton = b;
        }
        @Override
        public void onClick(View v) {
            Intent intent = new Intent(MainActivity.this, PostFormItemActivity.class);
            intent.putExtra(FROM_TITLE, _myButton.getTitle());
            MainActivity.this.startActivity(intent);
        }
    }
    private void configureActionsMenu(FloatingActionsMenu menuMultipleActions) {
        FloatingActionButton fab = ((FloatingActionButton)menuMultipleActions.findViewById(R.id.action_humans));
        fab.setOnClickListener(new MyActionListener(fab));
        fab.setIconDrawable(new IconDrawable(this, FontAwesomeIcons.fa_users).colorRes(R.color.white).actionBarSize());

        fab = ((FloatingActionButton)menuMultipleActions.findViewById(R.id.action_news));
        fab.setOnClickListener(new MyActionListener(fab));
        fab.setIconDrawable(new IconDrawable(this, FontAwesomeIcons.fa_newspaper_o).colorRes(R.color.white).actionBarSize());

        fab = ((FloatingActionButton)menuMultipleActions.findViewById(R.id.action_causes));
        fab.setOnClickListener(new MyActionListener(fab));
        fab.setIconDrawable(new IconDrawable(this, FontAwesomeIcons.fa_hand_o_down).colorRes(R.color.white).actionBarSize());

        fab = ((FloatingActionButton)menuMultipleActions.findViewById(R.id.action_jobs));
        fab.setOnClickListener(new MyActionListener(fab));
        fab.setIconDrawable(new IconDrawable(this, FontAwesomeIcons.fa_briefcase).colorRes(R.color.white).actionBarSize());

        fab = ((FloatingActionButton)menuMultipleActions.findViewById(R.id.action_bites));
        fab.setOnClickListener(new MyActionListener(fab));
        fab.setIconDrawable(new IconDrawable(this, FontAwesomeIcons.fa_spoon).colorRes(R.color.white).actionBarSize());
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.nav_profile) {
            // Handle the camera action
        } else if (id == R.id.nav_like) {

        } else if (id == R.id.nav_rewards) {

        } else if (id == R.id.nav_bookmark) {

        } else if (id == R.id.nav_share) {

        } else if (id == R.id.nav_rateus) {

        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
}
